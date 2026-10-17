import asyncio
import re

from anki_parser.anki.schemas import AnkiNote

from .service import AnkiService, anki_service


class CacheService:
    def __init__(self, service: AnkiService) -> None:
        self.service = service
        self.cached_backs: set[str] = set()
        self._is_initialized: bool = False

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
        self._is_initialized = True

    async def exists(self, back: str) -> bool:
        if not self._is_initialized:
            await self.warm_up()
        return self._normalize(back) in self.cached_backs

    async def add(self, back: str) -> None:
        if not self._is_initialized:
            await self.warm_up()
        self.cached_backs.add(self._normalize(back))


anki_cache = CacheService(anki_service)
