from __future__ import annotations

from PySide6.QtWidgets import QSystemTrayIcon, QWidget


class NotificationService:
    def __init__(self, parent: QWidget) -> None:
        self.tray = QSystemTrayIcon(parent)
        self.tray.setToolTip("YouTube Downloader")
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray.show()

    def show(self, title: str, message: str) -> None:
        if self.tray.isVisible():
            self.tray.showMessage(title, message, QSystemTrayIcon.Information, 5000)
