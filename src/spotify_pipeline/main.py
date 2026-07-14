# src/spotify_pipeline/main.py
from spotify_pipeline.extract.auth import get_spotify_token
from spotify_pipeline.utils.spotify_client import get_tracks
from spotify_pipeline.extract.artists import extract_artists
from spotify_pipeline.extract.albums import extract_albums
from spotify_pipeline.extract.tracks import extract_tracks
from spotify_pipeline.load.s3 import save_to_bronze
from spotify_pipeline.utils.logger import get_logger

logger = get_logger(__name__)


def run_pipeline():
    """
    Main pipeline orchestrator.
    Bronze layer: Extract from Spotify API → Save raw JSON to S3
    """
    logger.info("Starting Spotify pipeline")

    # Step 1: Get token
    token = get_spotify_token()

    # Step 2: Fetch raw data (one API call)
    items = get_tracks(token)

    # Step 3: Extract each entity
    artists = extract_artists(items)
    albums = extract_albums(items)
    tracks = extract_tracks(items)

    # Step 4: Save to S3 Bronze layer
    save_to_bronze(artists, "artists")
    save_to_bronze(albums, "albums")
    save_to_bronze(tracks, "tracks")

    logger.info("Pipeline complete ✅")


if __name__ == "__main__":
    run_pipeline()