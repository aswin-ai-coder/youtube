from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QSystemTrayIcon, QWidget


class NotificationService:
    def __init__(self, parent: QWidget) -> None:
        self.tray = QSystemTrayIcon(parent)

        icon_path = (
            Path(__file__).resolve().parents[2]
            / "assets"
            / "icons"
            / "icon.png"
        )

        if icon_path.exists():
            self.tray.setIcon(QIcon(str(icon_path)))

        self.tray.setToolTip("YouTube Downloader")

        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray.show()

    def show(self, title: str, message: str) -> None:
        if self.tray.isVisible():
            self.tray.showMessage(
                title,
                message,
                QSystemTrayIcon.Information,
                5000,
            )
