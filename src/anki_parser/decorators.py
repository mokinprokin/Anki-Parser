from functools import wraps
from typing import Any

from anki_parser.core.exceptions import AnkiAPIError, AnkiConnectionError
from anki_parser.core.logger import logger


def handle_anki_errors(func):
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> str:
        try:
            return await func(*args, **kwargs)
        except (AnkiConnectionError, AnkiAPIError) as exc:
            error_msg = f"Error executing '{func.__name__}': {exc}"
            logger.error(error_msg)
            raise
        except Exception:
            logger.exception("Unexpected error in '%s'", func.__name__)
            raise

    return wrapper
