from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)


class SettingsDialog(QDialog):
    def __init__(self, settings: dict[str, Any]) -> None:
        super().__init__()
        self.setWindowTitle("Settings")
        self.setMinimumWidth(560)
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        self.theme_combo.setCurrentText(settings.get("theme", "dark"))
        self.accent_input = QLineEdit(settings.get("accent_color", "#2563eb"))
        self.language_input = QLineEdit(settings.get("language", "en"))
        self.filename_input = QLineEdit(settings.get("filename_template", "%(title)s.%(ext)s"))
        self.concurrent_downloads = self._spin(settings.get("concurrent_downloads", 2), 1, 8)
        self.max_retries = self._spin(settings.get("max_retries", 10), 1, 50)
        self.concurrent_fragments = self._spin(settings.get("concurrent_fragments", 4), 1, 16)
        self.folder_input = QLineEdit(settings.get("download_folder", str(Path.home() / "Downloads")))
        self.ffmpeg_input = QLineEdit(settings.get("ffmpeg_path", ""))
        self.update_channel = QComboBox()
        self.update_channel.addItems(["stable", "beta"])
        self.update_channel.setCurrentText(settings.get("update_channel", "stable"))

        form.addRow(QLabel("Theme"), self.theme_combo)
        form.addRow(QLabel("Accent color"), self.accent_input)
        form.addRow(QLabel("Language"), self.language_input)
        form.addRow(QLabel("Filename template"), self.filename_input)
        form.addRow(QLabel("Concurrent downloads"), self.concurrent_downloads)
        form.addRow(QLabel("Max retries"), self.max_retries)
        form.addRow(QLabel("Concurrent fragments"), self.concurrent_fragments)
        form.addRow(QLabel("Download folder"), self._path_row(self.folder_input, self._browse_folder))
        form.addRow(QLabel("FFmpeg path"), self._path_row(self.ffmpeg_input, self._browse_ffmpeg))
        form.addRow(QLabel("Update channel"), self.update_channel)
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def values(self) -> dict[str, Any]:
        return {
            "theme": self.theme_combo.currentText(),
            "accent_color": self.accent_input.text().strip() or "#2563eb",
            "language": self.language_input.text().strip() or "en",
            "download_folder": self.folder_input.text().strip(),
            "filename_template": self.filename_input.text().strip() or "%(title)s.%(ext)s",
            "concurrent_downloads": self.concurrent_downloads.value(),
            "max_retries": self.max_retries.value(),
            "concurrent_fragments": self.concurrent_fragments.value(),
            "ffmpeg_path": self.ffmpeg_input.text().strip(),
            "update_channel": self.update_channel.currentText(),
        }

    def _path_row(self, line_edit: QLineEdit, callback) -> QHBoxLayout:
        row = QHBoxLayout()
        row.addWidget(line_edit, 1)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(callback)
        row.addWidget(browse_btn)
        return row

    def _browse_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Choose download folder", self.folder_input.text())
        if folder:
            self.folder_input.setText(folder)

    def _browse_ffmpeg(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Choose FFmpeg executable", self.ffmpeg_input.text())
        if path:
            self.ffmpeg_input.setText(path)

    def _spin(self, value: int, minimum: int, maximum: int) -> QSpinBox:
        spin = QSpinBox()
        spin.setRange(minimum, maximum)
        spin.setValue(int(value))
        return spin
