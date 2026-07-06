from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QApplication

from app.core.history_service import HistoryService


class HistoryActions:
    def __init__(self, history: HistoryService) -> None:
        self.history = history

    def open_file(self, record_id: int) -> None:
        if record := self.history.get(record_id):
            path = Path(record.get("output_path") or "")
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def open_folder(self, record_id: int) -> None:
        if record := self.history.get(record_id):
            path = Path(record.get("output_path") or "")
            folder = path if path.is_dir() else path.parent
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))

    def copy_url(self, record_id: int) -> None:
        if record := self.history.get(record_id):
            QApplication.clipboard().setText(record["url"])
