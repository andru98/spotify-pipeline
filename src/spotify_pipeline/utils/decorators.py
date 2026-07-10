# src/spotify_pipeline/utils/decorators.py
import time
import functools
from spotify_pipeline.utils.logger import get_logger

logger = get_logger(__name__)


def log_execution(func):
    """
    Logs function start, completion, and duration.
    Separates logging infrastructure from business logic.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Starting {func.__name__}")
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            duration = time.perf_counter() - start
            logger.info(f"Completed {func.__name__} in {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.perf_counter() - start
            logger.error(f"Failed {func.__name__} after {duration:.2f}s: {e}")
            raise

    return wrapper


def retry(max_attempts: int = 3, exceptions: tuple = (Exception,)):
    """
    Retries function on transient failures with exponential backoff.
    Only retries on specified exception types.

    Usage:
        @retry(max_attempts=3, exceptions=(ConnectionError, TimeoutError))
        def fetch_data(): ...
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        logger.error(
                            f"{func.__name__} failed after "
                            f"{max_attempts} attempts: {e}"
                        )
                        raise
                    wait = 2 ** attempt  # exponential backoff: 1s, 2s, 4s
                    logger.warning(
                        f"{func.__name__} attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {wait}s..."
                    )
                    time.sleep(wait)

        return wrapper

    return decorator