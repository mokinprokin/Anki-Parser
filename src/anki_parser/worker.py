import asyncio

import pyperclip

from anki_parser.anki.cache import anki_cache
from anki_parser.anki.manager import manager
from anki_parser.anki.parser import ClipboardParser
from anki_parser.core.http_client import http_client
from anki_parser.core.logger import logger
from anki_parser.core.toast import notifier
from anki_parser.core.utils import app_lifespan


async def poll_clipboard() -> None:
    logger.info("Clipboard listener active...")
    last_processed = ""

    while True:
        try:
            current_clipboard = str(pyperclip.paste())
            if current_clipboard != last_processed and ClipboardParser.might_contain_cards(current_clipboard):
                last_processed = current_clipboard

                batch = await manager.prepare_batch(current_clipboard)

                if not batch or not batch.has_new_cards:
                    if batch and batch.skipped_duplicates > 0:
                        notifier.notify_duplicates_skipped(batch.skipped_duplicates)
                    pyperclip.copy("")
                    last_processed = ""
                    continue

                await notifier.prompt_batch_confirmation(
                    batch=batch,
                    on_confirm=manager.commit_batch,
                )
                pyperclip.copy("")
                last_processed = ""

        except Exception as exc: #noqa
            logger.error("Clipboard loop fault: %s", exc)

        await asyncio.sleep(1)


async def run_worker() -> None:
    async with app_lifespan(http_client, anki_cache):
        notifier.notify_active(len(anki_cache.cached_backs))
        await poll_clipboard()


if __name__ == "__main__":
    asyncio.run(run_worker())