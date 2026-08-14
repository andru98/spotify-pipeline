import sys
import boto3
import json
import os
sys.path.insert(0, '/var/task')
from spotify_pipeline.load.s3 import read_bronze, get_s3_client
from spotify_pipeline.transform.artists import transform_artists, save_artists_silver
from spotify_pipeline.transform.albums import transform_albums, save_albums_silver
from spotify_pipeline.transform.tracks import transform_tracks, save_tracks_silver
from spotify_pipeline.gold.top_artists import top_artists
from spotify_pipeline.gold.album_stats import album_stats
from spotify_pipeline.gold.explicit_analysis import build_explicit_analysis
from spotify_pipeline.gold.save_gold import save_to_gold
from spotify_pipeline.utils.logger import get_logger
from spotify_pipeline.config import config


logger = get_logger(__name__)

def lambda_handler(event, context):
    try:
        # Get trigger info from S3 event
        s3_key = event['Records'][0]['s3']['object']['key']
        bucket = event['Records'][0]['s3']['bucket']['name']
        logger.info(f"Triggered by: {s3_key}")

        # Read trigger file
        s3 = get_s3_client()
        trigger = json.loads(
            s3.get_object(Bucket=bucket, Key=s3_key)['Body'].read()
        )
        logger.info(f"Processing date: {trigger['date']}")


        run_date = trigger['date']

        artists_raw = read_bronze("artists", date=run_date)
        albums_raw = read_bronze("albums", date=run_date)
        tracks_raw = read_bronze("tracks", date=run_date)

        # Step 2: Transform Silver
        save_artists_silver(transform_artists(artists_raw))
        save_albums_silver(transform_albums(albums_raw))
        save_tracks_silver(transform_tracks(tracks_raw))

        # Step 3: Build Gold
        save_to_gold(top_artists(), "top_artists")
        save_to_gold(album_stats(), "album_stats")
        save_to_gold(build_explicit_analysis(), "explicit_analysis")

        logger.info("Transform + Gold complete ✅")
        return {"statusCode": 200, "body": "Transform complete"}

    except Exception as e:
        logger.error(f"Transform failed: {str(e)}")
        raise