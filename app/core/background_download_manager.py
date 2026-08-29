from __future__ import annotations


class BackgroundDownloadManager:
    """Small lifecycle facade for an already-created download coordinator."""

    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.running = False

    def start(self):
        self.running = True
        self.coordinator.start_available()

    def stop(self):
        self.running = False
        self.coordinator.shutdown()

    def add(self, item):
        self.coordinator.add(item)
