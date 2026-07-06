from __future__ import annotations

from pathlib import Path
from threading import Thread
from typing import Any

from app.core.download_service import DownloadService
from app.core.models import DownloadOptions, QueueStatus
from app.core.queue_service import QueueItem, QueueService
from app.core.settings_service import SettingsService


class MobileDownloadWorker(Thread):
    def __init__(
        self,
        item: QueueItem,
        options: DownloadOptions,
        manager: "MobileDownloadManager",
    ) -> None:
        super().__init__(daemon=True)
        self.item = item
        self.options = options
        self.manager = manager
        self.cancelled = False

    def run(self) -> None:
        def hook(data: dict[str, Any]) -> None:
            if self.cancelled:
                raise RuntimeError("Download cancelled")

        try:
            self.manager.queue.update(self.item.id, status=QueueStatus.RUNNING)
            DownloadService().download(self.options, hook)
            self.manager.queue.update(
                self.item.id, status=QueueStatus.COMPLETED, progress=100
            )
        except Exception as exc:
            item = self.manager.queue.get(self.item.id)
            if self.cancelled and item and item.status == QueueStatus.PAUSED:
                self.manager.queue.update(self.item.id, error=str(exc))
            else:
                self.manager.queue.update(
                    self.item.id, status=QueueStatus.FAILED, error=str(exc)
                )
        finally:
            self.manager.active = max(0, self.manager.active - 1)
            self.manager.workers.pop(self.item.id, None)
            self.manager.start_available()

    def stop(self) -> None:
        self.cancelled = True


class MobileDownloadManager:
    def __init__(self) -> None:
        self.queue = QueueService()
        self.settings = SettingsService()
        self.active = 0
        self.workers: dict[str, MobileDownloadWorker] = {}

    def enqueue(self, item: QueueItem) -> None:
        self.queue.enqueue(item)
        self.start_available()

    def start_available(self) -> None:
        limit = int(self.settings.get("concurrent_downloads", 2))
        while len(self.workers) < limit and self.queue.due_count() > 0:
            item = self.queue.dequeue()
            if item is None:
                return
            worker = MobileDownloadWorker(item, self._options(item), self)
            self.workers[item.id] = worker
            worker.start()

    def pause(self, item_id: str) -> None:
        item = self.queue.get(item_id)
        if not item:
            return
        item.status = QueueStatus.PAUSED
        if worker := self.workers.get(item_id):
            worker.stop()

    def resume(self, item_id: str) -> None:
        if self.queue.update(item_id, status=QueueStatus.QUEUED) is not None:
            self.start_available()

    def cancel(self, item_id: str) -> None:
        item = self.queue.get(item_id)
        if not item:
            return
        item.status = QueueStatus.CANCELLED
        if worker := self.workers.get(item_id):
            worker.stop()

    def retry(self, item_id: str) -> bool:
        if self.queue.retry(item_id):
            self.start_available()
            return True
        return False

    def _options(self, item: QueueItem) -> DownloadOptions:
        return DownloadOptions(
            url=item.url,
            output_dir=Path(item.output_dir),
            kind=item.kind,
            quality=item.quality,
            audio_codec=item.audio_codec,
            audio_bitrate=item.audio_bitrate,
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


mobile_manager = MobileDownloadManager()
