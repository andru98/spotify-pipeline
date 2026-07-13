# src/spotify_pipeline/extract/tracks.py
from spotify_pipeline.utils.logger import get_logger

logger = get_logger(__name__)


def extract_tracks(items: list) -> list:
    track_list = []

    for track in items:          # ← no item["track"] now
        track_dict = {
            "track_id":    track["id"],
            "name":        track["name"],
            "duration_ms": track["duration_ms"],
            "popularity":  track.get("popularity", 0),
            "url":         track["external_urls"]["spotify"],
            "album_id":    track["album"]["id"],
            "artist_id":   track["album"]["artists"][0]["id"]
        }
        track_list.append(track_dict)

    logger.info(f"Extracted {len(track_list)} tracks")
    return track_list
