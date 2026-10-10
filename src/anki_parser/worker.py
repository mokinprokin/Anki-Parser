import asyncio
import pyperclip

from anki_parser.anki.cache import anki_cache
from anki_parser.anki.manager import manager
from anki_parser.anki.parser import ClipboardParser
from anki_parser.core.http_client import http_client
from anki_parser.core.logger import logger
from anki_parser.core.utils import app_lifespan, show_toast


async def poll_clipboard() -> None:
    logger.info("Clipboard listener active. Awaiting payload...")
    last_processed = ""

    while True:
        try:
            current_clipboard = str(pyperclip.paste())
            if current_clipboard != last_processed:
                if ClipboardParser.might_contain_cards(current_clipboard):
                    last_processed = current_clipboard
                    added, skipped = await manager.process_payload(current_clipboard)

                    if added > 0 or skipped > 0:
                        show_toast(
                            "Anki Agent",
                            f"Saved: {added} | Duplicates skipped: {skipped}",
                        )

                    pyperclip.copy("")
                    last_processed = ""

        except Exception as exc:
            logger.info("Transient clipboard read fault: %s", exc)

        await asyncio.sleep(1)


async def run_worker() -> None:
    async with app_lifespan(http_client, anki_cache):
        show_toast("Anki Agent Active", f"Cached {len(anki_cache.cached_backs)} cards.")
        await poll_clipboard()


if __name__ == "__main__":
    asyncio.run(run_worker())
