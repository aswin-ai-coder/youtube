from __future__ import annotations

from pathlib import Path
from threading import Lock, Thread
from typing import Callable

from app.core.download_engine import DownloadEngine
from app.core.models import DownloadOptions, QueueStatus
from app.core.queue_service import QueueItem, QueueService


class Event:
    def __init__(self) -> None:
        self._callbacks: list[Callable] = []

    def connect(self, callback: Callable) -> None:
        self._callbacks.append(callback)

    def emit(self, *args) -> None:
        for callback in tuple(self._callbacks):
            try:
                callback(*args)
            except Exception:
                pass


class AndroidDownloadCoordinator:
    """Kivy-safe download coordinator with no Qt dependency."""

    def __init__(self, queue: QueueService, settings) -> None:
        self.queue = queue
        self.settings = settings
        self.engine = DownloadEngine()
        self.workers: dict[str, Thread] = {}
        self.cancelled: set[str] = set()
        self.lock = Lock()
        self.queue_changed = Event()
        self.progress_changed = Event()
        self.status_changed = Event()
        self.completed = Event()
        self.failed = Event()
        self.speed_changed = Event()
        self.size_changed = Event()
        self.eta_changed = Event()

    def add(self, item: QueueItem) -> None:
        self.queue.enqueue(item)
        self.queue_changed.emit()
        self.start_available()

    def start_available(self) -> None:
        limit = max(1, int(self.settings.get("concurrent_downloads", 2)))
        with self.lock:
            active = len(self.workers)
        while active < limit:
            item = self.queue.dequeue()
            if item is None:
                break
            thread = Thread(target=self._run_item, args=(item,), daemon=True)
            with self.lock:
                self.workers[item.id] = thread
            thread.start()
            active += 1
        self.queue_changed.emit()

    def _run_item(self, item: QueueItem) -> None:
        def hook(data):
            if item.id in self.cancelled:
                raise RuntimeError("Download cancelled")
            status = data.get("status")
            if status == "downloading":
                downloaded = data.get("downloaded_bytes", 0) or 0
                total = data.get("total_bytes") or data.get("total_bytes_estimate") or 0
                progress = min(100, int(downloaded * 100 / total)) if total else 0
                self.queue.update(item.id, status=QueueStatus.RUNNING, progress=progress)
                self.progress_changed.emit(item.id, progress)
                speed = data.get("speed") or 0
                eta = data.get("eta") or 0
                self.speed_changed.emit(item.id, f"{speed / 1024 / 1024:.2f} MB/s" if speed else "--")
                self.size_changed.emit(item.id, f"{downloaded / 1024 / 1024:.1f} MB", f"{total / 1024 / 1024:.1f} MB" if total else "--")
                self.eta_changed.emit(item.id, f"{eta}s" if eta else "--")
                self.status_changed.emit(item.id, "Downloading")
            elif status == "finished":
                self.status_changed.emit(item.id, "Finalizing...")

        try:
            options = self._options(item)
            self.engine.download(options, hook)
            self.queue.update(item.id, status=QueueStatus.COMPLETED, progress=100)
            self.completed.emit(item.id, str(options.output_dir))
        except Exception as exc:
            status = QueueStatus.CANCELLED if item.id in self.cancelled else QueueStatus.FAILED
            self.queue.update(item.id, status=status, error=str(exc))
            if status == QueueStatus.FAILED:
                self.failed.emit(item.id, str(exc))
        finally:
            with self.lock:
                self.workers.pop(item.id, None)
                self.cancelled.discard(item.id)
            self.queue_changed.emit()
            self.start_available()

    def _options(self, item: QueueItem) -> DownloadOptions:
        return DownloadOptions(
            url=item.url,
            output_dir=Path(item.output_dir),
            kind=item.kind,
            quality=item.quality,
            audio_bitrate=item.audio_bitrate,
            audio_codec=item.audio_codec,
            video_codec=item.video_codec,
            container=item.container,
            filename_template=item.filename_template,
            subtitle_languages=item.subtitle_languages,
            write_subtitles=item.write_subtitles,
            write_auto_subtitles=item.write_auto_subtitles,
            translate_subtitles=item.translate_subtitles,
            translation_language=item.translation_language,
            subtitle_format=item.subtitle_format,
            embed_subtitles=item.embed_subtitles,
            embed_thumbnail=item.embed_thumbnail if hasattr(item, "embed_thumbnail") else True,
            embed_metadata=item.embed_metadata if hasattr(item, "embed_metadata") else True,
            playlist=item.playlist,
            playlist_items=item.playlist_items,
            max_retries=int(self.settings.get("max_retries", 10)),
            concurrent_fragments=int(self.settings.get("concurrent_fragments", 4)),
            ffmpeg_path=self.settings.get("ffmpeg_path") or None,
        )

    def pause(self, item_id: str) -> None:
        self.cancel(item_id, QueueStatus.PAUSED)

    def cancel(self, item_id: str, final_status: QueueStatus = QueueStatus.CANCELLED) -> None:
        self.cancelled.add(item_id)
        item = self.queue.get(item_id)
        if item and not self.workers.get(item_id):
            self.queue.update(item_id, status=final_status)
        self.queue_changed.emit()

    def resume(self, item_id: str) -> None:
        if self.queue.get(item_id):
            self.cancelled.discard(item_id)
            self.queue.update(item_id, status=QueueStatus.QUEUED, progress=0, error=None)
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
        for item_id in list(self.workers):
            self.cancel(item_id)
