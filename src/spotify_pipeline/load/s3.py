# src/spotify_pipeline/load/s3.py
import json
import boto3
from datetime import datetime
from spotify_pipeline.config import config
from spotify_pipeline.utils.logger import get_logger
from spotify_pipeline.utils.decorators import retry, log_execution

logger = get_logger(__name__)


def get_s3_client():
    """Create boto3 S3 client using credentials from config."""
    return boto3.client(
        "s3",
        region_name=config.aws_region,
        aws_access_key_id=config.aws_access_key_id,
        aws_secret_access_key=config.aws_secret_access_key
    )


@log_execution
@retry(max_attempts=3, exceptions=(Exception,))
def save_to_bronze(data: list, entity: str) -> str:
    """
    Save raw JSON data to S3 Bronze layer.
    Bronze = raw, append-only, never modified.

    Path: s3://bucket/bronze/entity/YYYY/MM/DD/HHMMSS.json
    """
    s3 = get_s3_client()
    now = datetime.utcnow()

    # Date partitioned key — easy Athena partition pruning
    key = (
        f"bronze/{entity}/"
        f"{now.year}/{now.month:02d}/{now.day:02d}/"
        f"{now.strftime('%H%M%S')}.json"
    )

    # Upload JSON to S3 Bronze bucket
    s3.put_object(
        Bucket=config.aws_bucket_raw,
        Key=key,
        Body=json.dumps(data, indent=2),
        ContentType="application/json"
    )

    logger.info(
        f"Saved {len(data)} {entity} records to "
        f"s3://{config.aws_bucket_raw}/{key}"
    )
    return key