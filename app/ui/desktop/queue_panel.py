from __future__ import annotations
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QListWidget, QPushButton
from PySide6.QtWidgets import QVBoxLayout

from app.core.queue_service import QueueItem


class QueuePanel(QFrame):
    pause_requested = Signal(str)
    resume_requested = Signal(str)
    cancel_requested = Signal(str)
    retry_requested = Signal(str)
    remove_requested = Signal(str)
    move_requested = Signal(str, int)

    def __init__(self) -> None:
        super().__init__()
        self._ids: list[str] = []
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Download Queue"))
        self.queue_list = QListWidget()
        layout.addWidget(self.queue_list)
        actions = QHBoxLayout()
        for text, callback in [
            ("Pause", self._pause),
            ("Resume", self._resume),
            ("Cancel", self._cancel),
            ("Retry", self._retry),
            ("Remove", self._remove),
            ("Up", lambda: self._move(-1)),
            ("Down", lambda: self._move(1)),
        ]:
            button = QPushButton(text)
            button.clicked.connect(callback)
            actions.addWidget(button)
        layout.addLayout(actions)

    def set_queue_items(self, items: list[QueueItem]) -> None:
        self._ids = [item.id for item in items]
        self.queue_list.clear()
        for item in items:
            title = item.title or item.url
            details = [
                title,
                item.kind.value.replace("_", " ").title(),
                f"Status: {item.status.value.title()}",
                f"Progress: {item.progress}%",
            ]
            if item.scheduled_at:
                details.append(
                    f"Starts: {item.scheduled_at.strftime('%Y-%m-%d %H:%M')}"
                )
            if item.subtitle_languages:
                details.append(f"Subs: {','.join(item.subtitle_languages)}")
            if item.playlist:
                details.append("Playlist Download")
            self.queue_list.addItem(" | ".join(details))

    def selected_id(self) -> str | None:
        row = self.queue_list.currentRow()
        if row < 0 or row >= len(self._ids):
            return None
        return self._ids[row]

    def _pause(self) -> None:
        if item_id := self.selected_id():
            self.pause_requested.emit(item_id)

    def _resume(self) -> None:
        if item_id := self.selected_id():
            self.resume_requested.emit(item_id)

    def _cancel(self) -> None:
        if item_id := self.selected_id():
            self.cancel_requested.emit(item_id)

    def _retry(self) -> None:
        if item_id := self.selected_id():
            self.retry_requested.emit(item_id)

    def _remove(self) -> None:
        if item_id := self.selected_id():
            self.remove_requested.emit(item_id)

    def _move(self, offset: int) -> None:
        if item_id := self.selected_id():
            self.move_requested.emit(item_id, offset)
