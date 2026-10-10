from __future__ import annotations
import html
import re
from win11toast import toast
from contextlib import asynccontextmanager
from pathlib import Path
from typing import TYPE_CHECKING
import winsound
from .logger import logger

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


def show_toast(title: str, message: str, is_error: bool = False) -> None:
    if is_error:
        winsound.MessageBeep(winsound.MB_ICONHAND)
    else:
        winsound.MessageBeep(winsound.MB_OK)

    try:
        toast(
            title=title,
            body=message,
            app_id="Anki Agent",
            duration="short",
            icon=LOCAL_ICON_PATH,
        )
    except Exception as exc:
        logger.error("Failed to display Windows notification: %s", exc)


def load_file(file_name: str) -> str:
    file_path = Path(__file__).parent / file_name
    return file_path.read_text(encoding="utf-8").strip()


@asynccontextmanager
async def app_lifespan(http_client: HttpClient, cache: CacheService):
    logger.info("Initializing HTTP client and connection pool...")
    try:
        await http_client.start()
        await cache.warm_up()
        yield
    finally:
        logger.info("Shutting down HTTP client...")
        await http_client.close()
