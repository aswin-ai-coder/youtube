from __future__ import annotations

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QPlainTextEdit
from PySide6.QtWidgets import QVBoxLayout

from app.utils.validators import is_supported_url


class BatchUrlDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add Batch URLs")
        self.setMinimumSize(560, 420)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Enter one YouTube URL per line."))
        self.text_edit = QPlainTextEdit()
        layout.addWidget(self.text_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def urls(self) -> list[str]:
        urls: list[str] = []
        for line in self.text_edit.toPlainText().splitlines():
            url = line.strip()
            if url and is_supported_url(url):
                urls.append(url)
        return urls
