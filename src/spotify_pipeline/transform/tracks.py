import pandas as pd
import boto3
import io
from datetime import datetime
from spotify_pipeline.utils.logger import get_logger
from spotify_pipeline.utils.decorators import log_execution,retry
from spotify_pipeline.transform.quality import run_quality_checks
from spotify_pipeline.config import config

logger = get_logger(__name__)

@log_execution
def transform_tracks(track_list: list) -> pd.DataFrame:
    df = pd.DataFrame(track_list)
    df = df.dropna(subset=["track_id"])
    df = df.dropna(subset=["album_id", "artist_id"])
    df = df.drop_duplicates(subset=["track_id"])
    df["name"] = df["name"].str.strip()
    df["url"] = df["url"].str.strip()
    df = df.rename(columns={"url": "spotify_url"})
    df["duration_in_seconds"] = (df["duration_ms"] /1000).round(2)
    df["processed_at"] = datetime.utcnow()
    df["source"] = "spotify_search_api"
    run_quality_checks(df, "tracks", "track_id")
    return df

@log_execution
@retry(max_attempts = 3, exceptions = (Exception,))
def save_tracks_silver(df: pd.DataFrame) -> str:
    now = datetime.utcnow()
    key = (
        f"silver/tracks/"
        f"{now.year}/{now.month:02d}/{now.day:02d}/"
        f"tracks.parquet"
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

    logger.info(f"Saved silver tracks to s3://{config.aws_bucket_transformed}/{key}")
    return key

if __name__ == "__main__":
    from spotify_pipeline.extract.auth import get_spotify_token
    from spotify_pipeline.utils.spotify_client import get_tracks
    from spotify_pipeline.extract.tracks import extract_tracks

    token = get_spotify_token()
    items = get_tracks(token)
    tracks = extract_tracks(items)

    df = transform_tracks(tracks)
    print(df.head())
    print(df.dtypes)

    key = save_tracks_silver(df)
    print(f'Saved to: {key}')