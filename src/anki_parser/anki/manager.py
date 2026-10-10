from .cache import CacheService, anki_cache
from .parser import ClipboardParser
from .service import AnkiService, anki_service


class CardManager:
    def __init__(self, anki_service: AnkiService, cache: CacheService) -> None:
        self.anki_service = anki_service
        self.cache = cache

    async def process_payload(self, text: str) -> tuple[int, int]:
        requests = ClipboardParser.parse(text)

        if not requests:
            return 0, 0

        added_count = 0
        skipped_count = 0

        for req in requests:
            if self.cache.exists(req.back):
                skipped_count += 1
                continue

            await self.anki_service.add_note(req)
            self.cache.add(req.back)
            added_count += 1

        return added_count, skipped_count


manager = CardManager(anki_service, anki_cache)
