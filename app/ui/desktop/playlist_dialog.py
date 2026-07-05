from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QListWidget, QListWidgetItem
from PySide6.QtWidgets import QVBoxLayout


class PlaylistSelectionDialog(QDialog):
    def __init__(self, entries: list[dict], parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Select Playlist Videos")
        self.setMinimumSize(520, 520)
        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        for entry in entries:
            item = QListWidgetItem(f"{entry['index']}. {entry['title']}")
            item.setData(Qt.UserRole, str(entry["index"]))
            item.setCheckState(Qt.Checked)
            self.list_widget.addItem(item)
        layout.addWidget(self.list_widget)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def selected_indexes(self) -> list[str]:
        indexes: list[str] = []
        for row in range(self.list_widget.count()):
            item = self.list_widget.item(row)
            if item.checkState() == Qt.Checked:
                indexes.append(str(item.data(Qt.UserRole)))
        return indexes
