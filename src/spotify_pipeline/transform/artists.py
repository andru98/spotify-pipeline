import pandas as pd
import boto3
import io
from datetime import datetime
from spotify_pipeline.utils.logger import get_logger
from spotify_pipeline.utils.decorators import log_execution, retry
from spotify_pipeline.transform.quality import run_quality_checks
from spotify_pipeline.config import config

logger = get_logger(__name__)

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
    buffer = io.BytesIO()
    df.to_parquet(buffer , index=False)
    buffer.seek(0)

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

    logger.info(f"Saved silver artists to s3://{config.aws_bucket_transformed}/{key}")
    return key
if __name__ == "__main__":
    from spotify_pipeline.extract.auth import get_spotify_token
    from spotify_pipeline.utils.spotify_client import get_tracks
    from spotify_pipeline.extract.albums import extract_albums

    token = get_spotify_token()
    items = get_tracks(token)
    albums = extract_albums(items)

    df = transform_artists(albums)
    print(df.head())
    print(df.dtypes)

    key = save_artists_silver(df)
    print(f'Saved to: {key}')