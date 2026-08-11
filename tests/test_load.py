import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from spotify_pipeline.load.s3 import save_to_bronze
from spotify_pipeline.transform.artists import save_artists_silver
from spotify_pipeline.gold.save_gold import save_to_gold


# ============================================================
# Bronze Tests
# ============================================================

def test_save_to_bronze_calls_s3():
    """save_to_bronze calls S3 put_object exactly once."""
    with patch("spotify_pipeline.load.s3.boto3.client") as mock_boto:
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3

        save_to_bronze([{"artist_id": "123"}], "artists")

        mock_s3.put_object.assert_called_once()


def test_save_to_bronze_correct_bucket():
    """save_to_bronze uses raw S3 bucket."""
    with patch("spotify_pipeline.load.s3.boto3.client") as mock_boto:
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3

        save_to_bronze([{"artist_id": "123"}], "artists")

        call_args = mock_s3.put_object.call_args
        assert "spotify-raw-anna-2026" in str(call_args)


# ============================================================
# Silver Tests
# ============================================================

def test_save_artists_silver_calls_s3():
    """save_artists_silver calls S3 put_object exactly once."""
    with patch("spotify_pipeline.transform.artists.boto3.client") as mock_boto:
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3

        df = pd.DataFrame({
            "artist_id": ["123"],
            "name": ["Weeknd"],
            "spotify_url": ["http://..."],
            "processed_at": [pd.Timestamp.now()],
            "source": ["spotify_search_api"]
        })
        save_artists_silver(df)

        mock_s3.put_object.assert_called_once()


def test_save_artists_silver_correct_bucket():
    """save_artists_silver uses transformed S3 bucket."""
    with patch("spotify_pipeline.transform.artists.boto3.client") as mock_boto:
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3

        df = pd.DataFrame({
            "artist_id": ["123"],
            "name": ["Weeknd"],
            "spotify_url": ["http://..."],
            "processed_at": [pd.Timestamp.now()],
            "source": ["spotify_search_api"]
        })
        save_artists_silver(df)

        call_args = mock_s3.put_object.call_args
        assert "spotify-transform-anna-2026" in str(call_args)


# ============================================================
# Gold Tests
# ============================================================

def test_save_to_gold_calls_s3():
    """save_to_gold calls S3 put_object exactly once."""
    with patch("spotify_pipeline.gold.save_gold.boto3.client") as mock_boto:
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3

        df = pd.DataFrame({
            "artist_id": ["123"],
            "artist_name": ["Weeknd"],
            "track_count": [3]
        })
        save_to_gold(df, "top_artists")

        mock_s3.put_object.assert_called_once()


def test_save_to_gold_correct_bucket():
    """save_to_gold uses transformed S3 bucket."""
    with patch("spotify_pipeline.gold.save_gold.boto3.client") as mock_boto:
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3

        df = pd.DataFrame({
            "artist_id": ["123"],
            "artist_name": ["Weeknd"],
            "track_count": [3]
        })
        save_to_gold(df, "top_artists")

        call_args = mock_s3.put_object.call_args
        assert "spotify-transform-anna-2026" in str(call_args)


def test_save_to_gold_correct_entity_in_key():
    """save_to_gold uses entity name in S3 key path."""
    with patch("spotify_pipeline.gold.save_gold.boto3.client") as mock_boto:
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3

        df = pd.DataFrame({
            "artist_id": ["123"],
            "artist_name": ["Weeknd"],
            "track_count": [3]
        })
        save_to_gold(df, "top_artists")

        call_args = mock_s3.put_object.call_args
        assert "top_artists" in str(call_args)