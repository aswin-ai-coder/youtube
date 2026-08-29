from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import datetime
import json
from pathlib import Path
from threading import RLock
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
    embed_thumbnail: bool = True
    embed_metadata: bool = True
    thumbnail_url: str | None = None
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
    """Persistent, thread-safe download queue."""

    def __init__(self) -> None:
        self._queue: deque[QueueItem] = deque()
        self._lock = RLock()
        self.logger = get_logger("queue")
        self._data_dir = Path.home() / ".local" / "share" / "youtube-downloader"
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._queue_file = self._data_dir / "queue.json"
        self.load_queue()

    def save_queue(self) -> None:
        with self._lock:
            items = []
            for item in self._queue:
                if item.status == QueueStatus.COMPLETED:
                    continue
                data = asdict(item)
                data["status"] = item.status.value
                data["kind"] = item.kind.value
                if item.scheduled_at:
                    data["scheduled_at"] = item.scheduled_at.isoformat()
                items.append(data)
            temp = self._queue_file.with_suffix(".json.tmp")
            try:
                temp.write_text(
                    json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8"
                )
                temp.replace(self._queue_file)
            except Exception as exc:
                self.logger.error(f"Failed to save queue: {exc}")
                try:
                    temp.unlink(missing_ok=True)
                except OSError:
                    pass

    def load_queue(self) -> None:
        with self._lock:
            if not self._queue_file.exists():
                return
            try:
                data = json.loads(self._queue_file.read_text(encoding="utf-8"))
                if not isinstance(data, list):
                    raise ValueError("queue.json must contain a list")
                restored: deque[QueueItem] = deque()
                for raw in data:
                    if not isinstance(raw, dict):
                        continue
                    raw = dict(raw)
                    if raw.get("scheduled_at"):
                        raw["scheduled_at"] = datetime.fromisoformat(raw["scheduled_at"])
                    raw["status"] = QueueStatus(
                        raw.get("status", QueueStatus.QUEUED.value)
                    )
                    raw["kind"] = DownloadKind(
                        raw.get("kind", DownloadKind.VIDEO_AUDIO.value)
                    )
                    # Forward-compatible loading for queues created by older builds.
                    raw.setdefault("embed_thumbnail", True)
                    raw.setdefault("embed_metadata", True)
                    raw.setdefault("thumbnail_url", None)
                    item = QueueItem(**raw)
                    if item.status == QueueStatus.RUNNING:
                        item.status = QueueStatus.QUEUED
                    restored.append(item)
                self._queue = restored
            except Exception as exc:
                self.logger.error(f"Failed to load queue: {exc}")
                corrupt = self._queue_file.with_suffix(".json.corrupt")
                try:
                    self._queue_file.replace(corrupt)
                except OSError:
                    pass
                self._queue.clear()

    def enqueue(self, item: QueueItem) -> QueueItem:
        with self._lock:
            self._queue.append(item)
        self.save_queue()
        return item

    def extend(self, items: Iterable[QueueItem]) -> None:
        for item in items:
            self.enqueue(item)

    def dequeue(self) -> QueueItem | None:
        now = datetime.now()
        with self._lock:
            for item in self._queue:
                if (
                    item.status == QueueStatus.SCHEDULED
                    and item.scheduled_at
                    and item.scheduled_at <= now
                ):
                    item.status = QueueStatus.QUEUED
                if item.status == QueueStatus.QUEUED:
                    item.status = QueueStatus.RUNNING
                    break
            else:
                return None
        self.save_queue()
        return item

    def update(
        self,
        item_id: str,
        *,
        status: QueueStatus | None = None,
        progress: int | None = None,
        error: str | None = None,
        title: str | None = None,
        thumbnail_url: str | None = None,
    ) -> QueueItem | None:
        with self._lock:
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
            if thumbnail_url is not None:
                item.thumbnail_url = thumbnail_url
        self.save_queue()
        return item

    def retry(self, item_id: str) -> bool:
        with self._lock:
            item = self.get(item_id)
            if not item or item.status not in {
                QueueStatus.FAILED,
                QueueStatus.CANCELLED,
                QueueStatus.PAUSED,
            }:
                return False
            item.status, item.progress, item.error = QueueStatus.QUEUED, 0, None
        self.save_queue()
        return True

    def due_count(self) -> int:
        now = datetime.now()
        with self._lock:
            return sum(
                1
                for item in self._queue
                if item.status == QueueStatus.QUEUED
                or (
                    item.status == QueueStatus.SCHEDULED
                    and item.scheduled_at
                    and item.scheduled_at <= now
                )
            )

    def remove(self, item_id: str) -> bool:
        with self._lock:
            for index, item in enumerate(self._queue):
                if item.id == item_id:
                    del self._queue[index]
                    self.save_queue()
                    return True
        return False

    def move(self, item_id: str, offset: int) -> bool:
        with self._lock:
            items = list(self._queue)
            index = next(
                (i for i, item in enumerate(items) if item.id == item_id), -1
            )
            if index < 0:
                return False
            new_index = max(0, min(len(items) - 1, index + offset))
            items.insert(new_index, items.pop(index))
            self._queue = deque(items)
        self.save_queue()
        return True

    def get(self, item_id: str) -> QueueItem | None:
        with self._lock:
            return next((item for item in self._queue if item.id == item_id), None)

    def list_items(self) -> list[QueueItem]:
        with self._lock:
            return list(self._queue)

    def clear(self) -> None:
        with self._lock:
            self._queue.clear()
        self.save_queue()
