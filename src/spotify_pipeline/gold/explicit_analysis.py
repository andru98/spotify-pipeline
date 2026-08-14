import pandas as pd
import numpy as np
import boto3
import io
from datetime import datetime
from spotify_pipeline.config import config
from spotify_pipeline.utils.logger import get_logger
from spotify_pipeline.utils.decorators import log_execution, retry
from spotify_pipeline.load.s3 import get_s3_client
logger = get_logger(__name__)

def read_silver(entity: str) -> pd.DataFrame:
    s3 = get_s3_client()
    response = s3.list_objects_v2(
        Bucket=config.aws_bucket_transformed,
        Prefix=f"silver/{entity}/"
    )
    dfs = []
    for obj in response["Contents"]:
        # get file bytes from S3
        file = s3.get_object(
            Bucket=config.aws_bucket_transformed,
            Key=obj["Key"]
        )
        # load bytes into memory buffer
        buffer = io.BytesIO(file["Body"].read())

        # read parquet from buffer into DataFrame
        df = pd.read_parquet(buffer)

        print(f"Read: {obj['Key']} → shape: {df.shape}")

        # append to list
        dfs.append(df)
    combined:pd.DataFrame = pd.concat(dfs, ignore_index=True)
        # Sort by processed_at descending → keep latest
    if "processed_at" in combined.columns:
        combined = combined.sort_values("processed_at", ascending=False)

    combined = combined.drop_duplicates(
            subset=[f"{entity[:-1]}_id"],
            keep="first"  # ← keeps most recent version
        )
    return combined

@log_execution
def build_explicit_analysis() -> pd.DataFrame:
    tracks_df = read_silver("tracks")

    # cast explicit to int first
    tracks_df["explicit"] = pd.to_numeric(
            tracks_df["explicit"], errors="coerce"
         ).fillna(0).astype(int)

    total = len(tracks_df)
    explicit_count = tracks_df["explicit"].sum()
    clean_count = total - explicit_count

    result = pd.DataFrame({
            "total_tracks": [total],
            "explicit_count": [explicit_count],
            "clean_count": [clean_count],
            "explicit_pct": [round(explicit_count / total * 100, 2) if total > 0 else 0]
        })

    return result


@log_execution
@retry(max_attempts=3, exceptions=(Exception,))
def save_to_gold(df: pd.DataFrame, entity: str) -> str:
    now = datetime.utcnow()
    key = (
        f"gold/{entity}/"
        f"{now.year}/{now.month:02d}/{now.day:02d}/"
        f"{entity}.parquet"
    )

    s3 = boto3.client(
        "s3",
        region_name=config.aws_region,
        aws_access_key_id=config.aws_access_key_id,
        aws_secret_access_key=config.aws_secret_access_key
    )

    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False)
    buffer.seek(0)

    s3.put_object(
        Bucket=config.aws_bucket_transformed,
        Key=key,
        Body=buffer.getvalue(),
        ContentType="application/octet-stream"
    )

    logger.info(f"Saved gold {entity} to s3://{config.aws_bucket_transformed}/{key}")
    return key

if __name__ == "__main__":
    df = build_explicit_analysis()
    print(df)
