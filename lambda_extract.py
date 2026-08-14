import sys
import os
import json
sys.path.insert(0, '/var/task')

from spotify_pipeline.extract.auth import get_spotify_token
from spotify_pipeline.utils.spotify_client import get_tracks
from spotify_pipeline.extract.artists import extract_artists
from spotify_pipeline.extract.albums import extract_albums
from spotify_pipeline.extract.tracks import extract_tracks
from spotify_pipeline.load.s3 import save_to_bronze,get_s3_client
from spotify_pipeline.utils.logger import get_logger
from spotify_pipeline.config import config
from datetime import datetime
import boto3

logger = get_logger(__name__)

def lambda_handler(event, context):
    try:
        # Step 1: Extract
        token = get_spotify_token()
        items = get_tracks(token)

        artists = extract_artists(items)
        albums = extract_albums(items)
        tracks = extract_tracks(items)

        # Step 2: Save Bronze
        save_to_bronze(artists, "artists")
        save_to_bronze(albums, "albums")
        save_to_bronze(tracks, "tracks")

        # Step 3: Save trigger file → fires Transform Lambda
        now = datetime.utcnow()
        s3 = get_s3_client()
        s3.put_object(
            Bucket=config.aws_bucket_raw,
            Key=f"bronze/trigger/{now.year}/{now.month:02d}/{now.day:02d}/trigger.json",
            Body=json.dumps({
                "status": "extract_complete",
                "date": str(now.date()),
                "tracks_count": len(tracks),
                "artists_count": len(artists),
                "albums_count": len(albums)
            }),
            ContentType="application/json"
        )

        logger.info(f"Extract complete  {len(tracks)} tracks")
        return {"statusCode": 200, "body": "Extract complete"}

    except Exception as e:
        logger.error(f"Extract failed: {str(e)}")
        raise