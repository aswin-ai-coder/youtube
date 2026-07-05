from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QTimer, Signal

from core.download_service import DownloadWorker
from core.models import DownloadOptions, QueueStatus
from core.queue_service import QueueItem, QueueService


class DownloadCoordinator(QObject):
    queue_changed = Signal()
    progress_changed = Signal(int)
    status_changed = Signal(str)
    completed = Signal(str, str)
    failed = Signal(str, str)

    def __init__(self, queue: QueueService, settings, parent=None) -> None:
        super().__init__(parent)
        self.queue = queue
        self.settings = settings
        self.workers: dict[str, DownloadWorker] = {}
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.start_available)
        self.timer.start()

    def add(self, item: QueueItem) -> None:
        self.queue.enqueue(item)
        self.queue_changed.emit()
        self.start_available()

    def start_available(self) -> None:
        limit = int(self.settings.get("concurrent_downloads", 2))
        while len(self.workers) < limit and self.queue.due_count() > 0:
            item = self.queue.dequeue()
            if item is None:
                return
            self._start_item(item)
        self.queue_changed.emit()

    def pause(self, item_id: str) -> None:
        item = self.queue.update(item_id, status=QueueStatus.PAUSED)
        worker = self.workers.get(item_id)
        if worker:
            worker.stop()
        if item:
            item.error = None
        self.queue_changed.emit()

    def resume(self, item_id: str) -> None:
        self.queue.update(item_id, status=QueueStatus.QUEUED, error="")
        self.start_available()

    def cancel(self, item_id: str) -> None:
        self.queue.update(item_id, status=QueueStatus.CANCELLED)
        worker = self.workers.get(item_id)
        if worker:
            worker.stop()
        self.queue_changed.emit()

    def retry(self, item_id: str) -> None:
        if self.queue.retry(item_id):
            self.start_available()
            self.queue_changed.emit()

    def remove(self, item_id: str) -> None:
        self.cancel(item_id)
        self.queue.remove(item_id)
        self.queue_changed.emit()

    def move(self, item_id: str, offset: int) -> None:
        if self.queue.move(item_id, offset):
            self.queue_changed.emit()

    def _start_item(self, item: QueueItem) -> None:
        worker = DownloadWorker(options=self._options(item))
        self.workers[item.id] = worker
        worker.progress.connect(
            lambda value, item_id=item.id: self._progress(item_id, value)
        )
        worker.status.connect(self.status_changed.emit)
        worker.finished.connect(
            lambda output, item_id=item.id: self._finished(item_id, output)
        )
        worker.error.connect(
            lambda message, item_id=item.id: self._error(item_id, message)
        )
        worker.start()

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
            playlist=item.playlist,
            playlist_items=item.playlist_items,
            max_retries=int(self.settings.get("max_retries", 10)),
            concurrent_fragments=int(self.settings.get("concurrent_fragments", 4)),
            ffmpeg_path=self.settings.get("ffmpeg_path") or None,
        )

    def _progress(self, item_id: str, value: int) -> None:
        self.queue.update(item_id, status=QueueStatus.RUNNING, progress=value)
        self.progress_changed.emit(value)
        self.queue_changed.emit()

    def _finished(self, item_id: str, output: str) -> None:
        self.workers.pop(item_id, None)
        item = self.queue.update(item_id, status=QueueStatus.COMPLETED, progress=100)
        self.completed.emit(item_id, output)
        self.queue_changed.emit()
        self.start_available()

    def _error(self, item_id: str, message: str) -> None:
        self.workers.pop(item_id, None)
        item = self.queue.get(item_id)
        if item and item.status in {QueueStatus.PAUSED, QueueStatus.CANCELLED}:
            self.queue_changed.emit()
            self.start_available()
            return
        self.queue.update(item_id, status=QueueStatus.FAILED, error=message)
        self.failed.emit(item_id, message)
        self.queue_changed.emit()
        self.start_available()
