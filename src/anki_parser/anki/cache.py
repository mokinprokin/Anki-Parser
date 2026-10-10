import asyncio
import re
from anki_parser.anki.schemas import AnkiNote
from .service import AnkiService, anki_service


class CacheService:
    def __init__(self, service: AnkiService) -> None:
        self.service = service
        self.cached_backs: set[str] = set()

    @staticmethod
    def _normalize(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip().lower()

    async def warm_up(self) -> None:
        decks = await self.service.get_deck_names()
        tasks = [self.service.get_deck_notes(deck) for deck in decks]
        notes_per_deck: list[list[AnkiNote]] = await asyncio.gather(*tasks)

        self.cached_backs.clear()

        for deck_notes in notes_per_deck:
            for note in deck_notes:
                back_value = note.fields.back
                if back_value:
                    self.cached_backs.add(self._normalize(back_value))

    def exists(self, back: str) -> bool:
        return self._normalize(back) in self.cached_backs

    def add(self, back: str) -> None:
        self.cached_backs.add(self._normalize(back))


anki_cache = CacheService(anki_service)
