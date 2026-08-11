import pytest
from unittest.mock import patch, MagicMock
from spotify_pipeline.extract.auth import get_spotify_token


def test_get_spotify_token_success():
    """get_spotify_token returns token on successful API call."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": "fake_token_123"}
    mock_response.raise_for_status.return_value = None

    with patch("spotify_pipeline.extract.auth.requests.post", return_value=mock_response):
        token = get_spotify_token()
        assert token == "fake_token_123"


def test_get_spotify_token_returns_string():
    """get_spotify_token always returns a string."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": "abc123"}
    mock_response.raise_for_status.return_value = None

    with patch("spotify_pipeline.extract.auth.requests.post", return_value=mock_response):
        token = get_spotify_token()
        assert isinstance(token, str)

