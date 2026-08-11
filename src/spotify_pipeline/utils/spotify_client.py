# src/spotify_pipeline/utils/spotify_client.py
# src/spotify_pipeline/utils/spotify_client.py
import requests
import json
from spotify_pipeline.utils.logger import get_logger
from spotify_pipeline.utils.decorators import retry, log_execution
from spotify_pipeline.config import config

logger = get_logger(__name__)
BASE_URL = "https://api.spotify.com/v1"

@log_execution
@retry(max_attempts=3, exceptions=(requests.exceptions.RequestException,))
def get_tracks(token: str) -> list:
    """
    Search for tracks using multiple queries.
    Returns combined list of unique tracks.
    """
    all_items = []
    seen_ids = set()

    for query in config.spotify_search_queries:
        response = requests.get(
            f"{BASE_URL}/search",
            headers={"Authorization": f"Bearer {token}"},
            params={
                "q": query,
                "type": "track",
                "limit": 10
            },
            timeout=30
        )
        response.raise_for_status()
        items = response.json()["tracks"]["items"]

        for item in items:
            if item["id"] not in seen_ids:
                seen_ids.add(item["id"])
                all_items.append(item)

        logger.info(f"Query '{query}': fetched {len(items)} tracks")

    logger.info(f"Total unique tracks: {len(all_items)}")
    return all_items

if __name__ == "__main__":
    import json
    from spotify_pipeline.extract.auth import get_spotify_token
    token = get_spotify_token()
    items = get_tracks(token)

    # See raw structure cleanly
    print(json.dumps(items[0], indent=2))
