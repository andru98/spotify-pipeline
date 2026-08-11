import pytest
from spotify_pipeline.extract.artists import extract_artists
from spotify_pipeline.extract.albums import extract_albums
from spotify_pipeline.extract.tracks import extract_tracks


# ============================================================
# Helper fake data
# ============================================================

def make_fake_items():
    return [
        {
            "id": "track1",
            "name": "Blinding Lights",
            "duration_ms": 200000,
            "popularity": 90,
            "external_urls": {"spotify": "http://spotify.com/track1"},
            "album": {
                "id": "album1",
                "name": "After Hours",
                "release_date": "2020-03-20",
                "total_tracks": 14,
                "external_urls": {"spotify": "http://spotify.com/album1"}
            },
            "artists": [
                {
                    "id": "artist1",
                    "name": "The Weeknd",
                    "href": "http://spotify.com/artist1"
                }
            ],
            "explicit": True
        },
        {
            "id": "track2",
            "name": "Stay",
            "duration_ms": 180000,
            "popularity": 85,
            "external_urls": {"spotify": "http://spotify.com/track2"},
            "album": {
                "id": "album2",
                "name": "F*CK LOVE",
                "release_date": "2020-07-10",
                "total_tracks": 16,
                "external_urls": {"spotify": "http://spotify.com/album2"}
            },
            "artists": [
                {
                    "id": "artist1",  # same artist as track1 → dedup test
                    "name": "The Weeknd",
                    "href": "http://spotify.com/artist1"
                }
            ],
            "explicit": False
        }
    ]


# ============================================================
# Artist extraction tests
# ============================================================

def test_extract_artists_returns_list():
    """extract_artists returns a list."""
    items = make_fake_items()
    result = extract_artists(items)
    assert isinstance(result, list)


def test_extract_artists_deduplicates():
    """extract_artists removes duplicate artist_ids."""
    items = make_fake_items()
    result = extract_artists(items)
    assert len(result) == 1  # deduplicated


def test_extract_artists_correct_fields():
    """extract_artists returns correct field names."""
    items = make_fake_items()
    result = extract_artists(items)
    assert result[0]["artist_id"] == "artist1"
    assert result[0]["name"] == "The Weeknd"


# ============================================================
# Album extraction tests
# ============================================================

def test_extract_albums_returns_list():
    """extract_albums returns a list."""
    items = make_fake_items()
    result = extract_albums(items)
    assert isinstance(result, list)


def test_extract_albums_correct_count():
    """extract_albums returns correct number of unique albums."""
    items = make_fake_items()
    result = extract_albums(items)
    assert len(result) == 2


def test_extract_albums_correct_fields():
    """extract_albums returns correct field names."""
    items = make_fake_items()
    result = extract_albums(items)
    assert result[0]["album_id"] == "album1"
    assert result[0]["name"] == "After Hours"


# ============================================================
# Track extraction tests
# ============================================================

def test_extract_tracks_returns_list():
    """extract_tracks returns a list."""
    items = make_fake_items()
    result = extract_tracks(items)
    assert isinstance(result, list)


def test_extract_tracks_correct_count():
    """extract_tracks returns all tracks."""
    items = make_fake_items()
    result = extract_tracks(items)
    assert len(result) == 2


def test_extract_tracks_correct_fields():
    """extract_tracks returns correct field names."""
    items = make_fake_items()
    result = extract_tracks(items)
    assert result[0]["track_id"] == "track1"
    assert result[0]["name"] == "Blinding Lights"
    assert result[0]["explicit"] == True