# src/spotify_pipeline/main.py
from spotify_pipeline.extract.auth import get_spotify_token
from spotify_pipeline.utils.spotify_client import get_tracks
from spotify_pipeline.extract.artists import extract_artists
from spotify_pipeline.extract.albums import extract_albums
from spotify_pipeline.extract.tracks import extract_tracks
from spotify_pipeline.load.s3 import save_to_bronze
from spotify_pipeline.transform.artists import transform_artists, save_artists_silver
from spotify_pipeline.transform.albums import transform_albums, save_albums_silver
from spotify_pipeline.transform.tracks import transform_tracks, save_tracks_silver
from spotify_pipeline.gold.top_artists import top_artists
from spotify_pipeline.gold.album_stats import album_stats
from spotify_pipeline.gold.explicit_analysis import build_explicit_analysis
from spotify_pipeline.gold.save_gold import save_to_gold
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

    # Step 5: Transform Silver
    artists_df = transform_artists(artists)
    albums_df = transform_albums(albums)
    tracks_df = transform_tracks(tracks)

    # Step 6: Save Silver
    save_artists_silver(artists_df)
    save_albums_silver(albums_df)
    save_tracks_silver(tracks_df)

    # Step 7: Gold
    top_df = top_artists()
    album_df = album_stats()
    explicit_df = build_explicit_analysis()

    save_to_gold(top_df, "top_artists")
    save_to_gold(album_df, "album_stats")
    save_to_gold(explicit_df, "explicit_analysis")

    logger.info("Pipeline complete ✅")


if __name__ == "__main__":
    run_pipeline()