# src/spotify_pipeline/extract/albums.py
from spotify_pipeline.utils.logger import get_logger

logger = get_logger(__name__)


def extract_albums(items: list) -> list:
    album_list = []

    for track in items:
        album = track["album"]
        album_dict = {
            "album_id":     album["id"],
            "name":         album["name"],
            "release_date": album["release_date"],
            "total_tracks": album["total_tracks"],
            "url":          album["external_urls"]["spotify"]
        }
        album_list.append(album_dict)

    # Remove duplicates
    seen = set()
    unique_albums = []
    for album in album_list:
        if album["album_id"] not in seen:
            seen.add(album["album_id"])
            unique_albums.append(album)

    logger.info(f"Extracted {len(unique_albums)} unique albums")
    return unique_albums