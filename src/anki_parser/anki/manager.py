from anki_parser.anki.schemas import BatchPreview, NoteCreateRequest
from anki_parser.base import BaseExecutionComponent
from anki_parser.core.exceptions import AnkiAPIError, AnkiConnectionError

from .cache import CacheService, anki_cache
from .parser import ClipboardParser
from .service import AnkiService, anki_service


class CardManager(BaseExecutionComponent):
    def __init__(self, anki_service: AnkiService, cache: CacheService) -> None:
        self.anki_service = anki_service
        self.cache = cache

    async def prepare_batch(self, text: str) -> BatchPreview | None:
        requests = ClipboardParser.parse(text)
        if not requests:
            return None

        pending_cards: list[NoteCreateRequest] = []
        skipped_count = 0

        for req in requests:
            if await self.cache.exists(req.back):
                skipped_count += 1
            else:
                pending_cards.append(req)

        first_preview = "N/A"
        if pending_cards:
            raw_back = pending_cards[0].back.replace("\n", " ").strip()
            first_preview = (raw_back[:47] + "...") if len(raw_back) > 50 else raw_back

        self.logger.info(
            "Prepared batch: %d new, %d duplicates detected.",
            len(pending_cards),
            skipped_count,
        )

        return BatchPreview(
            total_parsed=len(requests),
            new_cards_count=len(pending_cards),
            skipped_duplicates=skipped_count,
            first_card_preview=first_preview,
            pending_cards=pending_cards,
        )

    async def commit_batch(self, batch: BatchPreview) -> int:
        added_count = 0
        self.logger.info(batch.first_card_preview)
        for req in batch.pending_cards:
            try:
                await self.anki_service.add_note(req)
                await self.cache.add(req.back)
                added_count += 1
            except AnkiAPIError as exc:
                self.logger.error("Skipping malformed card '%s': %s", req.front, exc)
            except AnkiConnectionError:
                self.logger.critical("Anki connection severed during batch commit.")
                raise

        self.logger.info("Committed %d cards to Anki.", added_count)
        return added_count


manager = CardManager(anki_service, anki_cache)
