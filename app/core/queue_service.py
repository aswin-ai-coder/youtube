from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable
from uuid import uuid4

from app.core.models import DownloadKind, QueueStatus


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

    def enqueue(self, item: QueueItem) -> QueueItem:
        self._queue.append(item)
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
        return item

    def retry(self, item_id: str) -> bool:
        item = self.get(item_id)
        if not item or item.status not in {QueueStatus.FAILED, QueueStatus.CANCELLED}:
            return False
        item.status = QueueStatus.QUEUED
        item.progress = 0
        item.error = None
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
        return True

    def get(self, item_id: str) -> QueueItem | None:
        return next((item for item in self._queue if item.id == item_id), None)

    def list_items(self) -> list[QueueItem]:
        return list(self._queue)

    def clear(self) -> None:
        self._queue.clear()
