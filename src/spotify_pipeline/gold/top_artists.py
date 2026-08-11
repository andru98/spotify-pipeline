import pandas as pd
import numpy as np
import boto3
import io
from datetime import datetime
from spotify_pipeline.config import config
from spotify_pipeline.utils.logger import get_logger
from spotify_pipeline.utils.decorators import log_execution, retry

logger = get_logger(__name__)

def read_silver(entity: str) -> pd.DataFrame:
    s3 = boto3.client(
        "s3",
        aws_access_key_id=config.aws_access_key_id,
        aws_secret_access_key=config.aws_secret_access_key,
        region_name=config.aws_region
    )
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
def top_artists()-> pd.DataFrame:
    artists_df = read_silver("artists")
    print(artists_df.columns.tolist())
    tracks_df = read_silver("tracks")
    print(tracks_df.columns.tolist())
    artists_df = artists_df.rename(columns={"name": "artist_name"})
    merged_df = pd.merge(artists_df, tracks_df, on="artist_id", how = 'left')
    merged_df["explicit"] = pd.to_numeric(
        merged_df["explicit"], errors="coerce"
    ).fillna(0).astype(int)
    agg_df = merged_df.groupby(
        ["artist_id", "artist_name"]
    ).agg(
          track_count =("track_id", "count"),
          avg_duration_seconds =("duration_in_seconds", "mean"),
          explicit_count=("explicit", "sum")
    ).reset_index()
    print(agg_df.columns.tolist())
    print("track_count values:", agg_df["track_count"].values)
    print("explicit_count values:", agg_df["explicit_count"].values)
    print("any zero track_count:", (agg_df["track_count"] == 0).any())
    agg_df["explicit_pct"] = np.where(
         agg_df["track_count"]>0,
        (agg_df["explicit_count"]/agg_df["track_count"] * 100).round(2), 0)
    agg_df = agg_df[agg_df["track_count"]>0]
    final_df = agg_df.sort_values("track_count", ascending=False)
    return final_df


if __name__ == "__main__":
    df = top_artists()
    print(df)
