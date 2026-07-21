import pandas as pd
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
        aws_access_key_id=config.S3_ACCESS_KEY_ID,
        aws_secret_access_key=config.S3_SECRET_ACCESS_KEY,
        region_name=config.S3_REGION_NAME
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
        combined =combined.drop_duplicates(subset = [f"{entity[:-1]}_id"])
        return combined