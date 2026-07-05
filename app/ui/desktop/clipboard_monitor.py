from __future__ import annotations

from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtWidgets import QApplication

from utils.validators import is_supported_url


class ClipboardMonitor(QObject):
    url_detected = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._last_clipboard = ""
        self.timer = QTimer(self)
        self.timer.setInterval(2000)
        self.timer.timeout.connect(self._watch)
        self.timer.start()

    def _watch(self) -> None:
        text = QApplication.clipboard().text().strip()
        if text != self._last_clipboard and is_supported_url(text):
            self._last_clipboard = text
            self.url_detected.emit(text)
