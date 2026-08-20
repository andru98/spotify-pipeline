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
def album_stats():
    albums_df = read_silver("albums")
    tracks_df = read_silver("tracks")
    albums_df = albums_df.rename(columns={"name": "album_name"})
    merged_df = pd.merge(albums_df, tracks_df, on = "album_id", how = "inner")
    agg_df = merged_df.groupby(
        ["album_id", "album_name", "release_date"]
    ).agg(
        total_tracks = ("total_tracks", "first"),
        track_count = ("track_id", "count"),
        avg_duration_seconds = ("duration_in_seconds", "mean"),
        explicit_count = ("explicit", "sum")
    ).reset_index()
    agg_df["release_year"] = pd.to_datetime(
        agg_df["release_date"], errors="coerce"
    ).dt.year.fillna(0).astype(int)
    agg_df = agg_df.sort_values("release_year", ascending=False)
    return agg_df


if __name__ == "__main__":
  df = album_stats()
  print (df.columns.tolist())
  print(df.head())
  print(df.dtypes)



