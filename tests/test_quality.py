import pytest
import pandas as pd
from datetime import datetime, timedelta
from spotify_pipeline.transform.quality import(
check_nulls,
check_duplicates,
check_row_count,
check_freshness,
run_quality_checks
)
'''
caplog is pytest's built-in log capture fixture — automatically injected when you add it as parameter. Captures all log messages during test so you can assert what was logged. No import needed.
'''

# Test 1: nulls exist → warning logged
def test_check_nulls_detects_nulls(caplog):
    df = pd.DataFrame({
        "artist_id": ["1", None, "3"],  # has null
    })
    with caplog.at_level("WARNING"):
        check_nulls(df, "artists")
    assert "nulls found" in caplog.text

# Test 2: no nulls → no warning
def test_check_nulls_no_nulls(caplog):
    df = pd.DataFrame({
        "artist_id": ["1", "2", "3"],  # no nulls
    })
    with caplog.at_level("WARNING"):
        check_nulls(df, "artists")
    assert "nulls found" not in caplog.text