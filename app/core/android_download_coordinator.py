from __future__ import annotations

from threading import Event as ThreadEvent, Lock, Thread
from typing import Callable

from app.core.android_service_launcher import AndroidServiceLauncher
from app.core.models import QueueStatus
from app.core.queue_service import QueueService


class Event:
    """Small callback event used by the Kivy UI without Qt."""

    def __init__(self) -> None:
        self._callbacks: list[Callable] = []

    def connect(self, callback: Callable) -> None:
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def emit(self, *args) -> None:
        for callback in tuple(self._callbacks):
            try:
                callback(*args)
            except Exception:
                pass


class AndroidDownloadCoordinator:
    """Coordinate the Android UI with the persistent background downloader service."""

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
        self._removed_ids: set[str] = set()
        self._last_state: dict[str, tuple] = {}
        self._monitor = Thread(target=self._monitor_queue, daemon=True)
        self._monitor.start()

    def add(self, item) -> None:
        self.queue.enqueue(item)
        self.queue_changed.emit()
        self.start_available()

    def start_available(self) -> None:
        if self.queue.due_count() <= 0:
            return
        self.service.start()
        self.queue_changed.emit()

    def _monitor_queue(self) -> None:
        while not self._stop_monitor.is_set():
            try:
                items = self.queue.list_items()
                current_ids = {item.id for item in items}

                for item in items:
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

                missing_ids = set(self._last_state) - current_ids
                for item_id in missing_ids:
                    previous = self._last_state.pop(item_id)
                    if item_id in self._removed_ids:
                        self._removed_ids.discard(item_id)
                        self._seen_terminal.discard(item_id)
                        continue

                    # QueueService intentionally removes completed entries from
                    # queue.json. Infer completion from the last observed RUNNING
                    # state so the UI still receives one completion event.
                    if previous and previous[0] == QueueStatus.RUNNING:
                        self._seen_terminal.add(item_id)
                        self.completed.emit(item_id, "")
                    self._seen_terminal.discard(item_id)

            except Exception:
                pass

            self._stop_monitor.wait(0.25)

    def _emit_item_state(self, item) -> None:
        self.progress_changed.emit(item.id, item.progress)
        self.status_changed.emit(item.id, self._status_text(item))
        self.speed_changed.emit(item.id, item.speed_text or "--")
        self.size_changed.emit(
            item.id,
            self._format_size(item.downloaded_bytes),
            self._format_size(item.total_bytes) if item.total_bytes else "--",
        )
        self.eta_changed.emit(
            item.id,
            "--" if item.eta_seconds is None else f"{item.eta_seconds}s",
        )

        if item.status == QueueStatus.COMPLETED and item.id not in self._seen_terminal:
            self._seen_terminal.add(item.id)
            self.completed.emit(item.id, item.output_dir)
        elif item.status == QueueStatus.FAILED and item.id not in self._seen_terminal:
            self._seen_terminal.add(item.id)
            self.failed.emit(item.id, item.error or "Download failed")
        elif item.status not in {QueueStatus.COMPLETED, QueueStatus.FAILED}:
            self._seen_terminal.discard(item.id)

    @staticmethod
    def _status_text(item) -> str:
        return {
            QueueStatus.QUEUED: "Queued",
            QueueStatus.SCHEDULED: "Scheduled",
            QueueStatus.RUNNING: "Downloading",
            QueueStatus.PAUSED: "Paused",
            QueueStatus.COMPLETED: "Completed",
            QueueStatus.FAILED: "Failed",
            QueueStatus.CANCELLED: "Cancelled",
        }.get(item.status, str(item.status))

    @staticmethod
    def _format_size(value: int) -> str:
        if value <= 0:
            return "0 B"
        size = float(value)
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if size < 1024 or unit == "TB":
                return f"{int(size)} B" if unit == "B" else f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def pause(self, item_id: str) -> None:
        if self.queue.get(item_id):
            self.queue.update(item_id, status=QueueStatus.PAUSED)
            self.queue_changed.emit()

    def cancel(self, item_id: str, final_status: QueueStatus = QueueStatus.CANCELLED) -> None:
        if self.queue.get(item_id):
            self.queue.update(
                item_id,
                status=final_status,
                error="" if final_status == QueueStatus.CANCELLED else None,
            )
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
        if not self.queue.get(item_id):
            return
        self._removed_ids.add(item_id)
        self.cancel(item_id)
        self.queue.remove(item_id)
        self._last_state.pop(item_id, None)
        self._seen_terminal.discard(item_id)
        self.queue_changed.emit()

    def move(self, item_id: str, offset: int) -> None:
        if self.queue.move(item_id, offset):
            self.queue_changed.emit()

    def shutdown(self) -> None:
        self._stop_monitor.set()
        self._monitor.join(timeout=1.0)
