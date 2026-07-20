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
def transform_albums(albums_list: list) -> pd.DataFrame:
    df = pd.DataFrame(albums_list)
    df = df.dropna(subset=["album_id"])
    df = df.drop_duplicates(subset=["album_id"])
    df["release_date"] = pd.to_datetime(df["release_date"], errors ="coerce")
    df["name"] = df["name"].str.strip()
    df["external_url"] = df["url"].str.strip()
    df = df.rename(columns={"url": "spotify_url"})
    df["processed_at"] = datetime.utcnow()
    df["source"] = "spotify_search_api"
    run_quality_checks(df, "albums", "album_id")
    return df

@log_execution
@retry(max_attempts = 3, exceptions = (Exception,))
def save_albums_silver(df: pd.DataFrame) -> str:
    now = datetime.utcnow()
    key = (
        f"silver/albums/"
        f"{now.year}/{now.month:02d}/{now.day:02d}/"
        f"albums.parquet"
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

    logger.info(f"Saved silver albums to s3://{config.aws_bucket_transformed}/{key}")
    return key

if __name__ == "__main__":
    from spotify_pipeline.extract.auth import get_spotify_token
    from spotify_pipeline.utils.spotify_client import get_tracks
    from spotify_pipeline.extract.albums import extract_albums

    token = get_spotify_token()
    items = get_tracks(token)
    albums = extract_albums(items)

    df = transform_albums(albums)
    print(df.head())
    print(df.dtypes)

    key = save_albums_silver(df)
    print(f'Saved to: {key}')