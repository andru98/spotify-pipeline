# src/spotify_pipeline/extract/artists.py
# src/spotify_pipeline/utils/spotify_client.py
# src/spotify_pipeline/extract/artists.py
from spotify_pipeline.utils.logger import get_logger

logger = get_logger(__name__)

def extract_artists(items: list) -> list:
    artist_list = []

    for track in items:
        for artist in track["artists"]:
            artist_dict = {
                "artist_id":    artist["id"],
                "name":         artist["name"],
                "external_url": artist["href"]
            }
            artist_list.append(artist_dict)

    # Remove duplicates
    seen = set()
    unique_artists = []
    for artist in artist_list:
        if artist["artist_id"] not in seen:
            seen.add(artist["artist_id"])
            unique_artists.append(artist)

    logger.info(f"Extracted {len(unique_artists)} unique artists")
    return unique_artists


