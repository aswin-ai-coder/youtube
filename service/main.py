"""Background downloader service entrypoint for python-for-android."""

import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event, Lock

from app.core.download_engine import DownloadEngine
from app.core.history_service import HistoryService
from app.core.models import DownloadOptions, QueueStatus
from app.core.queue_service import QueueItem, QueueService
from app.core.settings_service import SettingsService


class DownloadServiceProcess:
    """Process-safe queue consumer used by python-for-android services."""

    def __init__(self) -> None:
        self.queue = QueueService()
        self.settings = SettingsService()
        self.history = HistoryService()
        self.engine = DownloadEngine()
        self.stop_event = Event()
        self.lock = Lock()
        self.running: set[str] = set()

    def run(self) -> None:
        workers = max(1, int(self.settings.get("concurrent_downloads", 2)))
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = set()
            while not self.stop_event.is_set():
                self._reap(futures)
                while len(futures) < workers:
                    item = self.queue.dequeue()
                    if item is None:
                        break
                    self.running.add(item.id)
                    futures.add(pool.submit(self._download, item))
                time.sleep(0.5)

            for future in futures:
                try:
                    future.result(timeout=2)
                except Exception:
                    pass

    def stop(self) -> None:
        self.stop_event.set()

    def _reap(self, futures: set) -> None:
        done = {future for future in futures if future.done()}
        futures.difference_update(done)
        for future in done:
            try:
                future.result()
            except Exception:
                pass

    def _download(self, item: QueueItem) -> None:
        def hook(data: dict) -> None:
            current = self.queue.get(item.id)
            if not current or current.status in {QueueStatus.PAUSED, QueueStatus.CANCELLED}:
                raise RuntimeError("Download stopped")
            if data.get("status") == "downloading":
                downloaded = int(data.get("downloaded_bytes") or 0)
                total = int(data.get("total_bytes") or data.get("total_bytes_estimate") or 0)
                progress = int(downloaded * 100 / total) if total else 0
                self.queue.update(item.id, status=QueueStatus.RUNNING, progress=progress)

        try:
            current = self.queue.get(item.id)
            if not current or current.status != QueueStatus.RUNNING:
                return
            result = self.engine.download(self._options(item), hook)
            self.queue.update(item.id, status=QueueStatus.COMPLETED, progress=100, error="")
            self.history.add_record(
                title=item.title or item.url,
                url=item.url,
                output_path=result,
                thumbnail_url=item.thumbnail_url,
                status="completed",
            )
            self._notify("Download complete", item.title or item.url)
        except Exception as exc:
            current = self.queue.get(item.id)
            status = current.status if current and current.status in {QueueStatus.PAUSED, QueueStatus.CANCELLED} else QueueStatus.FAILED
            self.queue.update(item.id, status=status, error=str(exc))
            if status == QueueStatus.FAILED:
                self.history.add_record(
                    title=item.title or item.url,
                    url=item.url,
                    output_path=None,
                    thumbnail_url=item.thumbnail_url,
                    status="failed",
                )
                self._notify("Download failed", str(exc))
        finally:
            with self.lock:
                self.running.discard(item.id)

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


def main() -> None:
    DownloadServiceProcess().run()


if __name__ == "__main__":
    main()
