import pandas as pd
import boto3
import io
from datetime import datetime
from spotify_pipeline.utils.logger import get_logger
from spotify_pipeline.utils.decorators import log_execution
from spotify_pipeline.transform.quality import run_quality_checks
from spotify_pipeline import config

@log_execution
def transform_artists(artists_list: list) -> pd.DataFrame:
    df = pd.DataFrame(artists_list)
    df = df.dropna(subset=["artist_id"])
    df = df.drop_duplicates(subset=["artist_id"])
    df["name"] = df["name"].str.strip()
    df["external_url"] = df["external_url"].str.strip()
    df = df.rename(columns={"external_url": "spotify_url"})
    df["processed_at"] = datetime.utcnow()
    df["source"] = "spotify_search_api"
    run_quality_checks(df, "artists", "artist_id")
    return df

@log_execution
@retry(max_attempts = 3, exceptions = (Exception,))
def save_artists_silver(df: pd.DataFrame) -> str:
    now = datetime.utcnow()
    key = (
        f"silver/artists/"
        f"{now.year}/{now.month:02d}/{now.day:02d}/"
        f"artists.parquet"
    )
    s3 = boto3.client(
        "s3",
        region_name=config.aws_region,
        aws_access_key_id=config.aws_access_key_id,
        aws_secret_access_key=config.aws_secret_access_key
    )

    s3.put_object(
        Bucket=config.aws_bucket_transformed,
        Key=key,
        Body=buffer.getvalue(),
        ContentType="application/octet-stream"
    )