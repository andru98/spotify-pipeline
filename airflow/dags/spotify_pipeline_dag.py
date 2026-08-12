import sys
sys.path.insert(0, '/opt/airflow/spotify_src')

from airflow.sdk import dag, task
from datetime import datetime, timedelta
from spotify_pipeline.utils.logger import get_logger

logger = get_logger(__name__)

def notify_failure(context):
    task_id = context['task_instance'].task_id
    dag_id = context['dag'].dag_id
    execution_date = context['execution_date']
    exception = context.get('exception', 'Unknown error')

    logger.error(
        f"PIPELINE FAILED!\n"
        f"DAG: {dag_id}\n"
        f"Task: {task_id}\n"
        f"Date: {execution_date}\n"
        f"Error: {exception}"
    )

default_args = {
    "owner": "anna",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
    "on_failure_callback": notify_failure
}

@dag(
    dag_id="spotify_pipeline",
    default_args=default_args,
    description="Spotify data pipeline - Bronze, Silver, Gold",
    schedule="@daily",
    start_date=datetime(2026, 8, 5),
    catchup=False,
    tags=["spotify", "de", "portfolio"]
)
def spotify_pipeline():
    @task()
    def get_token():
        from spotify_pipeline.extract.auth import get_spotify_token
        return get_spotify_token()

    @task()
    def extract(token: str) -> dict:
        from spotify_pipeline.utils.spotify_client import get_tracks
        from spotify_pipeline.extract.artists import extract_artists
        from spotify_pipeline.extract.albums import extract_albums
        from spotify_pipeline.extract.tracks import extract_tracks

        items = get_tracks(token)
        return {
            "artists": extract_artists(items),
            "albums": extract_albums(items),
            "tracks": extract_tracks(items)
        }

    @task()
    def load_bronze(data: dict) -> None:
        from spotify_pipeline.load.s3 import save_to_bronze

        save_to_bronze(data["artists"], "artists")
        save_to_bronze(data["albums"], "albums")
        save_to_bronze(data["tracks"], "tracks")

    @task()
    def transform_silver(data: dict) -> str:
        from spotify_pipeline.transform.artists import transform_artists, save_artists_silver
        from spotify_pipeline.transform.albums import transform_albums, save_albums_silver
        from spotify_pipeline.transform.tracks import transform_tracks, save_tracks_silver

        save_artists_silver(transform_artists(data["artists"]))
        save_albums_silver(transform_albums(data["albums"]))
        save_tracks_silver(transform_tracks(data["tracks"]))
        return "silver_complete"

    @task()
    def build_gold(status: str) -> None:
        from spotify_pipeline.gold.top_artists import top_artists
        from spotify_pipeline.gold.album_stats import album_stats
        from spotify_pipeline.gold.explicit_analysis import build_explicit_analysis
        from spotify_pipeline.gold.save_gold import save_to_gold

        save_to_gold(top_artists(), "top_artists")
        save_to_gold(album_stats(), "album_stats")
        save_to_gold(build_explicit_analysis(), "explicit_analysis")

#Task dependencies
    token = get_token()
    data = extract(token)
    load_bronze(data)
    status = transform_silver(data)
    build_gold(status)

#Dag instantiation
spotify_pipeline()