from __future__ import annotations

from collections import deque
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable
from uuid import uuid4

from app.core.models import DownloadKind, QueueStatus
from app.utils.logger import get_logger


@dataclass(slots=True)
class QueueItem:
    url: str
    output_dir: str
    audio_only: bool = False
    quality: str = "Best"
    status: QueueStatus = QueueStatus.QUEUED
    id: str = field(default_factory=lambda: uuid4().hex)
    title: str | None = None
    progress: int = 0
    error: str | None = None
    kind: DownloadKind = DownloadKind.VIDEO_AUDIO
    audio_codec: str = "mp3"
    audio_bitrate: str = "320"
    container: str = "mp4"
    video_codec: str = "h264"
    filename_template: str = "%(title)s.%(ext)s"
    subtitle_languages: list[str] = field(default_factory=list)
    write_subtitles: bool = False
    write_auto_subtitles: bool = False
    translate_subtitles: bool = False
    translation_language: str = "en"
    subtitle_format: str = "srt"
    embed_subtitles: bool = False
    playlist: bool = False
    playlist_items: list[str] = field(default_factory=list)
    scheduled_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.audio_only:
            self.kind = DownloadKind.AUDIO
        if self.scheduled_at and self.status == QueueStatus.QUEUED:
            self.status = QueueStatus.SCHEDULED
        self.output_dir = str(Path(self.output_dir).expanduser())


class QueueService:
    """In-memory queue with stable ids and status updates."""

    def __init__(self) -> None:
        self._queue: deque[QueueItem] = deque()

        self.logger = get_logger("queue")

        self._data_dir = Path.home() / ".local" / "share" / "youtube-downloader"

        self._data_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._queue_file = self._data_dir / "queue.json"
        self.load_queue()

    def save_queue(self) -> None:
        """
        Save queue to disk.
        """

        items = []

        for item in self._queue:

            # Don't persist completed downloads.
            # They are already stored in History.
            if item.status == QueueStatus.COMPLETED:
                continue

            data = asdict(item)

            data["status"] = item.status.value
            data["kind"] = item.kind.value

            if item.scheduled_at:
                data["scheduled_at"] = item.scheduled_at.isoformat()

            items.append(data)

        try:
            with self._queue_file.open(
                "w",
                encoding="utf-8",
            ) as fp:
                json.dump(
                    items,
                    fp,
                    indent=4,
                    ensure_ascii=False,
                )

        except Exception as exc:
            self.logger.error(f"Failed to save queue: {exc}")

    def load_queue(self) -> None:
        """
        Restore queue from disk.
        """

        if not self._queue_file.exists():
            return

        try:
            with self._queue_file.open(
                "r",
                encoding="utf-8",
            ) as fp:
                items = json.load(fp)

            self._queue.clear()

            for data in items:

                if data.get("scheduled_at"):
                    data["scheduled_at"] = datetime.fromisoformat(data["scheduled_at"])

                data["status"] = QueueStatus(data["status"])
                data["kind"] = DownloadKind(data["kind"])

                item = QueueItem(**data)

                if item.status == QueueStatus.RUNNING:
                    item.status = QueueStatus.QUEUED

                self._queue.append(item)
        except Exception as exc:
            self.logger.error(f"Failed to load queue: {exc}")

    def enqueue(self, item: QueueItem) -> QueueItem:
        self._queue.append(item)
        self.save_queue()
        return item

    def extend(self, items: Iterable[QueueItem]) -> None:
        for item in items:
            self.enqueue(item)

    def dequeue(self) -> QueueItem | None:
        now = datetime.now()
        for item in self._queue:
            if item.status == QueueStatus.SCHEDULED and item.scheduled_at:
                if item.scheduled_at <= now:
                    item.status = QueueStatus.QUEUED
            if item.status == QueueStatus.QUEUED:
                item.status = QueueStatus.RUNNING
                self.save_queue()
                return item
        return None

    def update(
        self,
        item_id: str,
        *,
        status: QueueStatus | None = None,
        progress: int | None = None,
        error: str | None = None,
        title: str | None = None,
    ) -> QueueItem | None:
        item = self.get(item_id)
        if not item:
            return None
        if status is not None:
            item.status = status
        if progress is not None:
            item.progress = max(0, min(progress, 100))
        if error is not None:
            item.error = error
        if title is not None:
            item.title = title
        self.save_queue()
        return item

    def retry(self, item_id: str) -> bool:
        item = self.get(item_id)
        if not item or item.status not in {QueueStatus.FAILED, QueueStatus.CANCELLED}:
            return False
        item.status = QueueStatus.QUEUED
        item.progress = 0
        item.error = None

        self.save_queue()

        return True

    def due_count(self) -> int:
        now = datetime.now()
        return sum(
            1
            for item in self._queue
            if item.status == QueueStatus.QUEUED
            or (
                item.status == QueueStatus.SCHEDULED
                and item.scheduled_at is not None
                and item.scheduled_at <= now
            )
        )

    def remove(self, item_id: str) -> bool:
        for index, item in enumerate(self._queue):
            if item.id == item_id:
                del self._queue[index]
                self.save_queue()
                return True
        return False

    def move(self, item_id: str, offset: int) -> bool:
        items = list(self._queue)
        index = next((i for i, item in enumerate(items) if item.id == item_id), -1)
        if index < 0:
            return False
        new_index = max(0, min(len(items) - 1, index + offset))
        items.insert(new_index, items.pop(index))
        self._queue = deque(items)
        self.save_queue()
        return True

    def get(self, item_id: str) -> QueueItem | None:
        return next((item for item in self._queue if item.id == item_id), None)

    def list_items(self) -> list[QueueItem]:
        return list(self._queue)

    def clear(self) -> None:
        self._queue.clear()
        self.save_queue()
