from __future__ import annotations

from collections.abc import Callable

from kivy.clock import Clock
from kivy.core.clipboard import Clipboard


class ClipboardService:
    """Poll the clipboard for YouTube URLs when explicitly enabled."""

    def __init__(self, callback: Callable[[str], None], enabled: bool = True, interval: float = 1.0):
        self.callback = callback
        self.last_text = ""
        self.enabled = bool(enabled)
        self._event = Clock.schedule_interval(self.check, interval) if self.enabled else None

    def set_enabled(self, enabled: bool) -> None:
        enabled = bool(enabled)
        if enabled == self.enabled:
            return
        self.enabled = enabled
        if enabled:
            self._event = Clock.schedule_interval(self.check, 1.0)
        elif self._event is not None:
            self._event.cancel()
            self._event = None

    def check(self, dt) -> None:
        if not self.enabled:
            return
        try:
            text = Clipboard.paste().strip()
        except Exception:
            return
        if not text or text == self.last_text:
            return
        self.last_text = text
        if "youtube.com" in text or "youtu.be" in text:
            self.callback(text)

    def shutdown(self) -> None:
        if self._event is not None:
            self._event.cancel()
            self._event = None
