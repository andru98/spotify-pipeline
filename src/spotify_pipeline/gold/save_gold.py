

import pandas as pd
import boto3
import io
from datetime import datetime
from spotify_pipeline.config import config
from spotify_pipeline.utils.logger import get_logger
from spotify_pipeline.utils.decorators import log_execution, retry

logger = get_logger(__name__)

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
    from spotify_pipeline.gold.top_artists import top_artists
    from spotify_pipeline.gold.album_stats import album_stats
    from spotify_pipeline.gold.explicit_analysis import build_explicit_analysis

    top_artist_df = top_artists()
    album_df = album_stats()
    explicit_df = build_explicit_analysis()

    key1 = save_to_gold(top_artist_df, "top_artists")
    key2 = save_to_gold(album_df, "album_stats")
    key3 = save_to_gold(explicit_df, "explicit_analysis")

    print(f"top_artists: {key1}")
    print(f" album_stats: {key2}")
    print(f"explicit_analysis: {key3}")