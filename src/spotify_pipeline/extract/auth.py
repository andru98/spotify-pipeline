# src/spotify_pipeline/extract/auth.py
import base64
import requests
from spotify_pipeline.config import config
from spotify_pipeline.utils.logger import get_logger
from spotify_pipeline.utils.decorators import retry, log_execution

logger = get_logger(__name__)


@log_execution
@retry(max_attempts=3, exceptions=(requests.exceptions.RequestException,))
def get_spotify_token() -> str:
    """
    Get Spotify access token using Client Credentials flow.
    Server-to-server authentication — no user login needed.
    Token expires after 1 hour.
    """
    # Encode client_id:client_secret as base64
    credentials = f"{config.spotify_client_id}:{config.spotify_client_secret}"
    encoded = base64.b64encode(credentials.encode()).decode()

    response = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={"grant_type": "client_credentials"},
        timeout=30
    )
    response.raise_for_status()

    token = response.json()["access_token"]
    logger.info("Successfully obtained Spotify access token")
    return token