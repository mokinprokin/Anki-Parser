from __future__ import annotations

import html
import re
from contextlib import asynccontextmanager
from pathlib import Path
from typing import TYPE_CHECKING

from anki_parser.core.exceptions import AnkiConnectionError

from .logger import logger
from .toast import notifier

if TYPE_CHECKING:
    from anki_parser.anki.cache import CacheService

    from .http_client import HttpClient

icon_path = (
    Path(__file__).resolve().parent.parent.parent.parent / "assets" / "toast_img.jpg"
)
LOCAL_ICON_PATH = icon_path.as_uri()


def clean_html(raw_html: str) -> str:
    """Strip HTML tags, Angular attributes, and normalize whitespaces."""
    if not raw_html:
        return ""

    text = re.sub(r"<(br|p|div|li)[^>]*>", "\n", raw_html, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)

    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    return "\n".join(line for line in lines if line).strip()

def load_file(file_name: str) -> str:
    file_path = Path(__file__).parent / file_name
    return file_path.read_text(encoding="utf-8").strip()


@asynccontextmanager
async def app_lifespan(http_client: HttpClient, cache: CacheService):
    logger.info("Initializing HTTP client and connection pool...")
    try:
        await http_client.start()
        try:
            await cache.warm_up()
            logger.info("Cache warmed up successfully: %d items", len(cache.cached_backs))
        except AnkiConnectionError:
            logger.warning("Anki is not running at startup. Cache will be cold.")
            notifier.notify_error("Anki app didn't start. Please, open Anki to start working.", is_error=True)
        yield
    finally:
        logger.info("Shutting down HTTP client...")
        await http_client.close()
