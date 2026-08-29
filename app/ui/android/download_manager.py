from __future__ import annotations

from app.core.android_download_coordinator import AndroidDownloadCoordinator
from app.core.queue_service import QueueService
from app.core.settings_service import SettingsService


class AndroidDownloadManager:
    """Public Android download manager facade."""

    def __init__(self, settings=None, queue=None):
        self.settings = settings or SettingsService()
        self.queue = queue or QueueService()
        self.coordinator = AndroidDownloadCoordinator(self.queue, self.settings)

    def add(self, item):
        self.coordinator.add(item)

    def pause(self, item_id):
        self.coordinator.pause(item_id)

    def resume(self, item_id):
        self.coordinator.resume(item_id)

    def cancel(self, item_id):
        self.coordinator.cancel(item_id)

    def retry(self, item_id):
        self.coordinator.retry(item_id)

    def shutdown(self):
        self.coordinator.shutdown()
