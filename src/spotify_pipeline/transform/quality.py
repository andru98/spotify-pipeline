from datetime import datetime
import pandas as pd
from spotify_pipeline.utils.logger import get_logger


logger = get_logger(__name__)

def check_nulls(df: pd.DataFrame, entity:str)-> None:
    null_count = df.isnull().sum()
    for col, count in null_count.items():
        if count > 0:
            logger.warning(f"[{entity}] {col} : {count} nulls found!")
        else:
            logger.info (f"[{entity}] {col} has no null values!")

def check_duplicates(df:pd.DataFrame, entity:str, key:str )-> None:
    dupes = df.duplicated(subset=[key]).sum()
    if dupes > 0:
        logger.warning(f"[{entity}] {key} : {dupes} duplicates found!")
    else:
        logger.info (f"[{entity}] {key} has no duplicates!")

def check_row_count(df: pd.DataFrame, entity: str, min_rows: int,) -> None:
    row_count = len(df)
    if row_count == 0:
        logger.warning(f"[{entity}] has no rows!")
    elif row_count < min_rows:
        logger.warning(f"[{entity}] has {row_count} rows which is lower than {min_rows}")
    else:
        logger.warning(f"[{entity}] has {row_count} rows!")

def check_freshness(df: pd.DataFrame, entity: str, max_hours: int = 25) -> None:
    """Check data was processed within expected time window."""
    if "processed_at" not in df.columns:
        logger.warning(f"[{entity}] no processed_at column")
        return

    latest = pd.to_datetime(df["processed_at"]).max()
    hours_old = (datetime.utcnow() - latest.replace(tzinfo=None)).total_seconds() / 3600

    if hours_old > max_hours:
        logger.warning(f"[{entity}] data is {hours_old:.1f} hours old")
    else:
        logger.info(f"[{entity}] freshness OK — {hours_old:.1f} hours old")

def run_quality_checks(df, entity, key, min_rows=5):
    check_row_count(df, entity, min_rows)
    check_nulls(df, entity)
    check_duplicates(df, entity, key)
    check_freshness(df, entity)

if __name__ == "__main__":
    # sample data to test quality checks
    sample_artists = [
        {"artist_id": "123", "name": "The Weeknd", "external_url": "https://..."},
        {"artist_id": "456", "name": "Taylor Swift", "external_url": "https://..."},
        {"artist_id": "123", "name": "The Weeknd", "external_url": "https://..."},  # duplicate
        {"artist_id": None, "name": "Unknown", "external_url": None},  # null
    ]

    df = pd.DataFrame(sample_artists)
    print("Sample DataFrame:")
    print(df)
    print("\nRunning quality checks...")
    run_quality_checks(df, "artists", "artist_id", min_rows=3)