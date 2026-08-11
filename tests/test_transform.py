import pytest
import pandas as pd
from datetime import datetime
from spotify_pipeline.transform.artists import transform_artists
from spotify_pipeline.transform.albums import transform_albums
from spotify_pipeline.transform.tracks import transform_tracks

def test_transform_artists_strips_whitespace():
    """str.strip() removes leading/trailing whitespace from name."""
    raw = [
        {"artist_id": "123", "name": "  The Weeknd  ", "external_url": "http://..."}
    ]
    df = transform_artists(raw)
    assert df["name"].iloc[0] == "The Weeknd"

def test_transform_artists_drops_null_ids():
    """Rows with null artist_id should be dropped."""
    raw = [
        {"artist_id": "123", "name": "Weeknd", "external_url": "http://..."},
        {"artist_id": None, "name": "Unknown", "external_url": "http://..."}
    ]
    df = transform_artists(raw)
    assert len(df) == 1
    assert df["artist_id"].iloc[0] == "123"

def test_transform_artists_drops_duplicates():
    """Duplicate artist_ids should be removed keeping first."""
    raw = [
        {"artist_id": "123", "name": "Weeknd", "external_url": "http://..."},
        {"artist_id": "123", "name": "Weeknd", "external_url": "http://..."},  # duplicate
        {"artist_id": "456", "name": "Taylor", "external_url": "http://..."}
    ]
    df = transform_artists(raw)
    assert len(df) == 2

def test_transform_tracks_duration_seconds():
    """duration_in_seconds = duration_ms / 1000 rounded to 2dp."""
    raw = [
        {
            "track_id": "t1", "name": "Song", "duration_ms": 200000,
            "popularity": 80, "url": "http://...",
            "album_id": "a1", "artist_id": "ar1", "explicit": False
        }
    ]
    df = transform_tracks(raw)
    assert df["duration_in_seconds"].iloc[0] == 200.0

def test_transform_artists_adds_processed_at():
    """processed_at column should be added after transform."""
    raw = [
        {"artist_id": "123", "name": "Weeknd", "external_url": "http://..."}
    ]
    df = transform_artists(raw)
    assert "processed_at" in df.columns