# src/spotify_pipeline/utils/spotify_client.py
# src/spotify_pipeline/utils/spotify_client.py
import requests
import json
from spotify_pipeline.utils.logger import get_logger
from spotify_pipeline.utils.decorators import retry, log_execution

logger = get_logger(__name__)
BASE_URL = "https://api.spotify.com/v1"

@log_execution
@retry(max_attempts=3, exceptions=(requests.exceptions.RequestException,))
def get_tracks(token: str) -> list:
    """
    Search for tracks using Spotify Search API.
    Works with Client Credentials flow (no user auth needed).
    """
    response = requests.get(
        f"{BASE_URL}/search",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "q": "pop",
            "type": "track",
            "limit": 10
        },
        timeout=30
    )

    response.raise_for_status()
    items = response.json()["tracks"]["items"]
    print(items)
    print(items[0])
    logger.info(f"Fetched {len(items)} tracks from search")
    return items

if __name__ == "__main__":
    import json
    from spotify_pipeline.extract.auth import get_spotify_token
    token = get_spotify_token()
    items = get_tracks(token)

    # See raw structure cleanly
    print(json.dumps(items[0], indent=2))
