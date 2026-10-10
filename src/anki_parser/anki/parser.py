import re

from anki_parser.anki.schemas import NoteCreateRequest
from anki_parser.core.config import settings


class ClipboardParser:
    DECK_PATTERN = re.compile(r"===DECK:\s*(.+?)===")
    CARD_PATTERN = re.compile(
        r"===FRONT===\s*(.*?)\s*===BACK===\s*(.*?)\s*===END===", re.DOTALL
    )

    @classmethod
    def parse(cls, text: str) -> list[NoteCreateRequest]:
        if not text:
            return []

        deck_match = cls.DECK_PATTERN.search(text)
        target_deck = (
            deck_match.group(1).strip() if deck_match else settings.default_deck
        )

        matches = cls.CARD_PATTERN.findall(text)

        parsed_requests = []
        for front, back in matches:
            parsed_requests.append(
                NoteCreateRequest(
                    deck_name=target_deck,
                    front=front.strip(),
                    back=back.strip(),
                )
            )

        return parsed_requests

    @staticmethod
    def might_contain_cards(text: str) -> bool:
        return "===FRONT===" in text and "===BACK===" in text and "===END===" in text
