import winsound
from collections.abc import Callable
from pathlib import Path
from typing import Any

from win11toast import toast, toast_async

from anki_parser.anki.schemas import BatchPreview
from anki_parser.base import BaseExecutionComponent

ICON_PATH = Path(__file__).resolve().parent.parent.parent.parent / "assets" / "toast_img.jpg"
LOCAL_ICON = ICON_PATH.as_uri() if ICON_PATH.exists() else None


class ToastService(BaseExecutionComponent):
    def __init__(self) -> None:
        self._app_id = "Anki Agent"

    def _play_sound(self, is_error: bool = False) -> None:
        if is_error:
            winsound.MessageBeep(winsound.MB_ICONHAND)
        else:
            winsound.MessageBeep(winsound.MB_OK)

    def notify(self, title:str, body:str) -> None:
        self._play_sound(is_error=False)
        toast(
            title=title,
            body=body,
            app_id=self._app_id,
            icon=LOCAL_ICON,
            duration="short",
        )

    def notify_active(self, cached_count: int) -> None:
        self._play_sound(is_error=False)
        toast(
            title="Anki Agent Active",
            body=f"{cached_count} existing cards tracked.",
            app_id=self._app_id,
            icon=LOCAL_ICON,
            duration="short",
        )

    def notify_duplicates_skipped(self, skipped_count: int) -> None:
        self._play_sound(is_error=False)
        toast(
            title="Anki Agent",
            body=f"Skipped {skipped_count} duplicate card(s).",
            app_id=self._app_id,
            icon=LOCAL_ICON,
            duration="short",
        )

    async def notify_success(self, added_count: int, batch:BatchPreview) -> None:
        self._play_sound(is_error=False)
        body = (
            f"Successfully added {added_count} card(s) to Anki!\n"
            f"Preview: \"{batch.first_card_preview}\"\n"
            f"Deck: {batch.pending_cards[0].deck_name}"
        )
        toast(
            title="Import Completed",
            body=body,
            app_id=self._app_id,
            icon=LOCAL_ICON,
            duration="short",
        )

    def notify_error(self, message: str) -> None:
        self._play_sound(is_error=True)
        toast(
            title="Anki Agent Error",
            body=message,
            app_id=self._app_id,
            icon=LOCAL_ICON,
            button = "Cancel",
            duration="short",
        )

    async def prompt_batch_confirmation(
        self,
        batch: BatchPreview,
        on_confirm: Callable,
    ) -> None:
        self._play_sound(is_error=False)

        body_text = (
            f"Found {batch.new_cards_count} new card(s) (Skipped: {batch.skipped_duplicates})\n"
            f"Preview: \"{batch.first_card_preview}\"\n"
            f"Deck: {batch.pending_cards[0].deck_name}"
        )
        response: Any = await toast_async(
            title="Confirm Card Import?",
            body=body_text,
            app_id=self._app_id,
            icon=LOCAL_ICON,
            buttons=["Add","Dismiss"],
            duration="long",
        )
        if isinstance(response, dict) and "Add" in response.get("arguments"):
            added = await on_confirm(batch)
            self.notify_success(added)
        else:
            self.logger.info("Batch import dismissed or expired.%r", response)



notifier = ToastService()