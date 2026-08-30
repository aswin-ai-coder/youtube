from __future__ import annotations

import time
from threading import Event as ThreadEvent, Lock, Thread
from typing import Callable

from app.core.android_service_launcher import AndroidServiceLauncher
from app.core.models import QueueStatus
from app.core.queue_service import QueueService


class Event:
    """Tiny callback event used so the Android layer has no Qt dependency."""

    def __init__(self) -> None:
        self._callbacks: list[Callable] = []

    def connect(self, callback: Callable) -> None:
        self._callbacks.append(callback)

    def emit(self, *args) -> None:
        for callback in tuple(self._callbacks):
            try:
                callback(*args)
            except Exception:
                # A stale UI callback must never kill the queue monitor.
                pass


class AndroidDownloadCoordinator:
    """Android queue facade backed by a python-for-android foreground service."""

    def __init__(self, queue: QueueService, settings) -> None:
        self.queue = queue
        self.settings = settings
        self.service = AndroidServiceLauncher()
        self.lock = Lock()
        self.queue_changed = Event()
        self.progress_changed = Event()
        self.status_changed = Event()
        self.completed = Event()
        self.failed = Event()
        self.speed_changed = Event()
        self.size_changed = Event()
        self.eta_changed = Event()
        self._stop_monitor = ThreadEvent()
        self._seen_terminal: set[str] = set()
        self._last_state: dict[str, tuple] = {}
        self._monitor = Thread(target=self._monitor_queue, daemon=True)
        self._monitor.start()

    def add(self, item) -> None:
        self.queue.enqueue(item)
        self.queue_changed.emit()
        self.start_available()

    def start_available(self) -> None:
        # The foreground service owns the actual workers. Keeping this call
        # idempotent makes the UI safe to call after every enqueue/resume.
        self.service.start()
        self.queue_changed.emit()

    def _monitor_queue(self) -> None:
        while not self._stop_monitor.is_set():
            try:
                items = self.queue.list_items()
                current_ids = set()
                for item in items:
                    current_ids.add(item.id)
                    state = (
                        item.status,
                        item.progress,
                        item.downloaded_bytes,
                        item.total_bytes,
                        item.speed_text,
                        item.eta_seconds,
                        item.error,
                    )
                    if self._last_state.get(item.id) == state:
                        continue
                    self._last_state[item.id] = state
                    self._emit_item_state(item)

                # Drop stale snapshots after an item is removed.
                for item_id in set(self._last_state) - current_ids:
                    self._last_state.pop(item_id, None)
                    self._seen_terminal.discard(item_id)
            except Exception:
                pass
            self._stop_monitor.wait(0.25)

    def _emit_item_state(self, item) -> None:
        self.progress_changed.emit(item.id, item.progress)
        self.status_changed.emit(item.id, self._status_text(item))
        self.speed_changed.emit(item.id, item.speed_text or "--")
        downloaded = self._format_size(item.downloaded_bytes)
        total = self._format_size(item.total_bytes) if item.total_bytes else "--"
        self.size_changed.emit(item.id, downloaded, total)
        eta = "--" if item.eta_seconds is None else f"{item.eta_seconds}s"
        self.eta_changed.emit(item.id, eta)

        if item.status == QueueStatus.COMPLETED and item.id not in self._seen_terminal:
            self._seen_terminal.add(item.id)
            self.completed.emit(item.id, item.output_dir)
        elif item.status == QueueStatus.FAILED and item.id not in self._seen_terminal:
            self._seen_terminal.add(item.id)
            self.failed.emit(item.id, item.error or "Download failed")
        elif item.status not in {
            QueueStatus.COMPLETED,
            QueueStatus.FAILED,
        }:
            self._seen_terminal.discard(item.id)

    @staticmethod
    def _status_text(item) -> str:
        mapping = {
            QueueStatus.QUEUED: "Queued",
            QueueStatus.SCHEDULED: "Scheduled",
            QueueStatus.RUNNING: "Downloading",
            QueueStatus.PAUSED: "Paused",
            QueueStatus.COMPLETED: "Completed",
            QueueStatus.FAILED: "Failed",
            QueueStatus.CANCELLED: "Cancelled",
        }
        return mapping.get(item.status, str(item.status))

    @staticmethod
    def _format_size(value: int) -> str:
        if value <= 0:
            return "0 B"
        units = ("B", "KB", "MB", "GB", "TB")
        size = float(value)
        for unit in units:
            if size < 1024 or unit == units[-1]:
                return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
            size /= 1024
        return f"{size:.1f} TB"

    def pause(self, item_id: str) -> None:
        item = self.queue.get(item_id)
        if not item:
            return
        self.queue.update(item_id, status=QueueStatus.PAUSED)
        self.queue_changed.emit()
        self.start_available()

    def cancel(self, item_id: str, final_status: QueueStatus = QueueStatus.CANCELLED) -> None:
        if self.queue.get(item_id):
            self.queue.update(item_id, status=final_status, error="" if final_status == QueueStatus.CANCELLED else None)
        self.queue_changed.emit()

    def resume(self, item_id: str) -> None:
        if self.queue.get(item_id):
            self.queue.update(
                item_id,
                status=QueueStatus.QUEUED,
                progress=0,
                error=None,
                downloaded_bytes=0,
                total_bytes=0,
                speed_text="--",
                eta_seconds=None,
            )
            self.start_available()

    def retry(self, item_id: str) -> None:
        if self.queue.retry(item_id):
            self.start_available()

    def remove(self, item_id: str) -> None:
        self.cancel(item_id)
        self.queue.remove(item_id)
        self.queue_changed.emit()

    def move(self, item_id: str, offset: int) -> None:
        if self.queue.move(item_id, offset):
            self.queue_changed.emit()

    def shutdown(self) -> None:
        # Do not stop the foreground service here: the service is what keeps
        # downloads alive when Android backgrounds or kills the UI process.
        self._stop_monitor.set()
        self._monitor.join(timeout=1.0)
