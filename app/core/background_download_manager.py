from __future__ import annotations

from app.ui.desktop.download_coordinator import DownloadCoordinator


class BackgroundDownloadManager:

    def __init__(self, coordinator: DownloadCoordinator):

        self.coordinator = coordinator

        self.running = False

    def start(self):

        self.running = True

    def stop(self):

        self.running = False

    def add(self, item):

        self.coordinator.add(item)
