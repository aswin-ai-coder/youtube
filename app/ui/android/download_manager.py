from PySide6.QtCore import QObject, Signal

from app.core.queue_service import QueueService
from app.core.settings_service import SettingsService
from app.ui.desktop.download_coordinator import DownloadCoordinator


class AndroidDownloadManager(QObject):

    queue_changed = Signal()
    progress_changed = Signal(int)
    status_changed = Signal(str)
    completed = Signal(str, str)
    failed = Signal(str, str)

    def __init__(self):
        super().__init__()

        self.settings = SettingsService()
        self.queue = QueueService()

        self.coordinator = DownloadCoordinator(
            self.queue,
            self.settings,
            None,
        )

        self.coordinator.queue_changed.connect(self.queue_changed.emit)
        self.coordinator.progress_changed.connect(self.progress_changed.emit)
        self.coordinator.status_changed.connect(self.status_changed.emit)
        self.coordinator.completed.connect(self.completed.emit)
        self.coordinator.failed.connect(self.failed.emit)

    def add(self, item):
        self.coordinator.add(item)
