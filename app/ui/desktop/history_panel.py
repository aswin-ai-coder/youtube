from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
)


class HistoryPanel(QFrame):
    refresh_requested = Signal(str, str)
    open_file_requested = Signal(int)
    open_folder_requested = Signal(int)
    copy_url_requested = Signal(int)
    delete_requested = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        self._ids: list[int] = []
        self._records: list[dict] = []
        layout = QVBoxLayout(self)
        filters = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search history")
        self.search_input.textChanged.connect(self._refresh)
        self.status_filter = QComboBox()
        self.status_filter.addItems(["all", "completed", "failed", "cancelled"])
        self.status_filter.currentTextChanged.connect(self._refresh)
        filters.addWidget(self.search_input, 1)
        filters.addWidget(self.status_filter)
        layout.addLayout(filters)
        self.history_list = QListWidget()
        self.history_list.currentRowChanged.connect(self._update_details)
        layout.addWidget(self.history_list)
        self.details_label = QLabel("Select a history item to see details")
        self.details_label.setWordWrap(True)
        self.details_label.setMinimumHeight(80)
        layout.addWidget(self.details_label)
        actions = QHBoxLayout()
        for text, callback in [
            ("Open File", self._open_file),
            ("Open Folder", self._open_folder),
            ("Copy URL", self._copy_url),
            ("Delete", self._delete),
        ]:
            button = QPushButton(text)
            button.clicked.connect(callback)
            actions.addWidget(button)
        layout.addLayout(actions)

    def set_records(self, records: list[dict]) -> None:
        self._records = records
        self._ids = [int(record["id"]) for record in records]
        self.history_list.clear()
        for record in records:
            self.history_list.addItem(
                f"{record['date']} | {record['title']} | {record['status']}"
            )
        self._update_details()

    def selected_id(self) -> int | None:
        row = self.history_list.currentRow()
        if row < 0 or row >= len(self._ids):
            return None
        return self._ids[row]

    def _refresh(self) -> None:
        status = self.status_filter.currentText()
        self.refresh_requested.emit(
            self.search_input.text().strip(),
            "" if status == "all" else status,
        )

    def _update_details(self) -> None:
        if self.selected_id() is not None:
            row = self.history_list.currentRow()
            if row < 0 or row >= len(self._ids):
                return
            item = self._records[row]
            details = (
                f"Title: {item['title']}\n"
                f"URL: {item['url']}\n"
                f"Status: {item['status']}\n"
                f"Output: {item['output_path'] or '-'}\n"
                f"Date: {item['date']}\n"
                f"Size: {item['size_bytes'] or '-'}"
            )
            self.details_label.setText(details)
        else:
            self.details_label.setText("Select a history item to see details")

    def _open_file(self) -> None:
        if record_id := self.selected_id():
            self.open_file_requested.emit(record_id)

    def _open_folder(self) -> None:
        if record_id := self.selected_id():
            self.open_folder_requested.emit(record_id)

    def _copy_url(self) -> None:
        if record_id := self.selected_id():
            self.copy_url_requested.emit(record_id)

    def _delete(self) -> None:
        if record_id := self.selected_id():
            self.delete_requested.emit(record_id)
