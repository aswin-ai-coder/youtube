from __future__ import annotations

import os
from pathlib import Path
from threading import Lock, Thread
from typing import Any, Callable

from app.core.download_engine import DownloadEngine
from app.core.history_service import HistoryService
from app.core.models import DownloadKind, DownloadOptions, QueueStatus
from app.core.queue_service import QueueItem, QueueService
from app.core.settings_service import SettingsService


def _is_android_runtime() -> bool:
    return bool(os.environ.get("ANDROID_ARGUMENT"))


class MobileDownloadWorker(Thread):
    def __init__(self, item: QueueItem, manager: "MobileDownloadManager") -> None:
        super().__init__(daemon=True)
        self.item = item
        self.manager = manager
        self.cancelled = False

    def run(self) -> None:
        def hook(data: dict[str, Any]) -> None:
            current = self.manager.queue.get(self.item.id)
            if self.cancelled or not current or current.status in {
                QueueStatus.PAUSED,
                QueueStatus.CANCELLED,
            }:
                raise RuntimeError("Download stopped")
            status = data.get("status")
            if status == "downloading":
                downloaded = int(data.get("downloaded_bytes") or 0)
                total = int(data.get("total_bytes") or data.get("total_bytes_estimate") or 0)
                progress = int(downloaded * 100 / total) if total else 0
                self.manager.queue.update(
                    self.item.id,
                    status=QueueStatus.RUNNING,
                    progress=progress,
                )

        try:
            self.manager.queue.update(self.item.id, status=QueueStatus.RUNNING, error="")
            result = self.manager.engine.download(self.manager._options(self.item), hook)
            self.manager.queue.update(
                self.item.id,
                status=QueueStatus.COMPLETED,
                progress=100,
                error="",
            )
            self.manager.history.add_record(
                title=self.item.title or self.item.url,
                url=self.item.url,
                output_path=result,
                thumbnail_url=self.item.thumbnail_url,
                status="completed",
            )
            self.manager._notify("Download complete", self.item.title or self.item.url)
        except Exception as exc:
            current = self.manager.queue.get(self.item.id)
            if current and current.status in {QueueStatus.PAUSED, QueueStatus.CANCELLED}:
                status = current.status
            elif self.cancelled:
                status = QueueStatus.CANCELLED
            else:
                status = QueueStatus.FAILED
            self.manager.queue.update(self.item.id, status=status, error=str(exc))
            if status == QueueStatus.FAILED:
                self.manager.history.add_record(
                    title=self.item.title or self.item.url,
                    url=self.item.url,
                    output_path=None,
                    thumbnail_url=self.item.thumbnail_url,
                    status="failed",
                )
                self.manager._notify("Download failed", str(exc))
        finally:
            with self.manager.lock:
                self.manager.workers.pop(self.item.id, None)
            self.manager.start_available()

    def stop(self) -> None:
        self.cancelled = True


class MobileDownloadManager:
    """Shared mobile queue facade.

    On Android, Buildozer's background service owns actual downloads. When the
    UI is run outside Android, local threads are used so the mobile UI remains
    usable for development and testing.
    """

    def __init__(self) -> None:
        self.queue = QueueService()
        self.settings = SettingsService()
        self.history = HistoryService()
        self.engine = DownloadEngine()
        self.workers: dict[str, MobileDownloadWorker] = {}
        self.lock = Lock()
        self._android_service = _is_android_runtime()

    def enqueue(self, item: QueueItem) -> None:
        self.queue.enqueue(item)
        self.start_available()

    def start_available(self) -> None:
        if self._android_service:
            return
        limit = max(1, int(self.settings.get("concurrent_downloads", 2)))
        with self.lock:
            active = len(self.workers)
        while active < limit and self.queue.due_count() > 0:
            item = self.queue.dequeue()
            if item is None:
                break
            worker = MobileDownloadWorker(item, self)
            with self.lock:
                self.workers[item.id] = worker
            worker.start()
            active += 1

    def pause(self, item_id: str) -> None:
        item = self.queue.get(item_id)
        if not item:
            return
        self.queue.update(item_id, status=QueueStatus.PAUSED)
        if worker := self.workers.get(item_id):
            worker.stop()

    def resume(self, item_id: str) -> None:
        if self.queue.update(item_id, status=QueueStatus.QUEUED, error=""):
            self.start_available()

    def cancel(self, item_id: str) -> None:
        item = self.queue.get(item_id)
        if not item:
            return
        self.queue.update(item_id, status=QueueStatus.CANCELLED)
        if worker := self.workers.get(item_id):
            worker.stop()

    def retry(self, item_id: str) -> bool:
        if self.queue.retry(item_id):
            self.start_available()
            return True
        return False

    def remove(self, item_id: str) -> bool:
        if worker := self.workers.get(item_id):
            worker.stop()
        return self.queue.remove(item_id)

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
            embed_thumbnail=item.embed_thumbnail,
            embed_metadata=item.embed_metadata,
            playlist=item.playlist,
            playlist_items=item.playlist_items,
            max_retries=int(self.settings.get("max_retries", 10)),
            concurrent_fragments=int(self.settings.get("concurrent_fragments", 4)),
            ffmpeg_path=self.settings.get("ffmpeg_path") or None,
        )

    def _notify(self, title: str, message: str) -> None:
        if not self.settings.get("notifications", True):
            return
        try:
            from app.core.notification_service import NotificationService

            NotificationService().notify(title, message)
        except Exception:
            pass


mobile_manager = MobileDownloadManager()
