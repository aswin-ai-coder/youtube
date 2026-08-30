from __future__ import annotations

from collections import deque
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime
import json
from pathlib import Path
from threading import RLock
from typing import Iterable, Iterator
from uuid import uuid4

from app.core.models import DownloadKind, QueueStatus
from app.utils.logger import get_logger

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows fallback
    fcntl = None


def _local_now() -> datetime:
    return datetime.now().astimezone()


def _normalize_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=_local_now().tzinfo)
    return value.astimezone()


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
        self.scheduled_at = _normalize_datetime(self.scheduled_at)
        if self.scheduled_at and self.status == QueueStatus.QUEUED:
            self.status = QueueStatus.SCHEDULED
        self.output_dir = str(Path(self.output_dir).expanduser())


class QueueService:
    """Persistent queue shared safely by UI and background processes."""

    def __init__(self, queue_file: str | Path | None = None) -> None:
        self._queue: deque[QueueItem] = deque()
        self._lock = RLock()
        self.logger = get_logger("queue")
        if queue_file is None:
            self._data_dir = Path.home() / ".local" / "share" / "youtube-downloader"
            self._queue_file = self._data_dir / "queue.json"
        else:
            self._queue_file = Path(queue_file).expanduser()
            self._data_dir = self._queue_file.parent
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._lock_file = self._queue_file.with_suffix(self._queue_file.suffix + ".lock")
        self.load_queue()

    @contextmanager
    def _process_lock(self) -> Iterator[None]:
        """Serialize queue file access across UI/service processes on POSIX."""
        if fcntl is None:
            yield
            return
        self._lock_file.parent.mkdir(parents=True, exist_ok=True)
        with self._lock_file.open("a+", encoding="utf-8") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    def _decode_items(self, data: object) -> deque[QueueItem]:
        if not isinstance(data, list):
            raise ValueError("queue.json must contain a list")
        restored: deque[QueueItem] = deque()
        for raw in data:
            if not isinstance(raw, dict):
                continue
            raw = dict(raw)
            if raw.get("scheduled_at"):
                raw["scheduled_at"] = datetime.fromisoformat(raw["scheduled_at"])
            raw["status"] = QueueStatus(raw.get("status", QueueStatus.QUEUED.value))
            raw["kind"] = DownloadKind(raw.get("kind", DownloadKind.VIDEO_AUDIO.value))
            raw.setdefault("embed_thumbnail", True)
            raw.setdefault("embed_metadata", True)
            raw.setdefault("thumbnail_url", None)
            item = QueueItem(**raw)
            if item.status == QueueStatus.RUNNING:
                item.status = QueueStatus.QUEUED
            restored.append(item)
        return restored

    def _read_queue_locked(self) -> deque[QueueItem]:
        if not self._queue_file.exists():
            return deque()
        try:
            data = json.loads(self._queue_file.read_text(encoding="utf-8"))
            return self._decode_items(data)
        except Exception as exc:
            self.logger.error(f"Failed to load queue: {exc}")
            corrupt = self._queue_file.with_suffix(".json.corrupt")
            try:
                self._queue_file.replace(corrupt)
            except OSError:
                pass
            return deque()

    def _serialize(self, queue: deque[QueueItem]) -> list[dict]:
        items: list[dict] = []
        for item in queue:
            if item.status == QueueStatus.COMPLETED:
                continue
            data = asdict(item)
            data["status"] = item.status.value
            data["kind"] = item.kind.value
            if item.scheduled_at:
                data["scheduled_at"] = item.scheduled_at.isoformat()
            items.append(data)
        return items

    def _write_queue_locked(self, queue: deque[QueueItem]) -> None:
        temp = self._queue_file.with_suffix(".json.tmp")
        temp.write_text(
            json.dumps(self._serialize(queue), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        temp.replace(self._queue_file)

    def save_queue(self) -> None:
        """Persist the current in-memory state for compatibility callers."""
        with self._lock, self._process_lock():
            try:
                self._write_queue_locked(self._queue)
            except Exception as exc:
                self.logger.error(f"Failed to save queue: {exc}")

    def load_queue(self) -> None:
        with self._lock, self._process_lock():
            self._queue = self._read_queue_locked()

    def enqueue(self, item: QueueItem) -> QueueItem:
        with self._lock, self._process_lock():
            queue = self._read_queue_locked()
            queue.append(item)
            self._write_queue_locked(queue)
            self._queue = queue
        return item

    def extend(self, items: Iterable[QueueItem]) -> None:
        values = list(items)
        if not values:
            return
        with self._lock, self._process_lock():
            queue = self._read_queue_locked()
            queue.extend(values)
            self._write_queue_locked(queue)
            self._queue = queue

    def dequeue(self) -> QueueItem | None:
        now = _local_now()
        with self._lock, self._process_lock():
            queue = self._read_queue_locked()
            selected = None
            for item in queue:
                if item.status == QueueStatus.SCHEDULED and item.scheduled_at and item.scheduled_at <= now:
                    item.status = QueueStatus.QUEUED
                if item.status == QueueStatus.QUEUED:
                    item.status = QueueStatus.RUNNING
                    selected = item
                    break
            if selected is None:
                self._queue = queue
                return None
            self._write_queue_locked(queue)
            self._queue = queue
            return selected

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
        with self._lock, self._process_lock():
            queue = self._read_queue_locked()
            item = next((entry for entry in queue if entry.id == item_id), None)
            if not item:
                self._queue = queue
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
            self._write_queue_locked(queue)
            self._queue = queue
            return item

    def retry(self, item_id: str) -> bool:
        with self._lock, self._process_lock():
            queue = self._read_queue_locked()
            item = next((entry for entry in queue if entry.id == item_id), None)
            if not item or item.status not in {QueueStatus.FAILED, QueueStatus.CANCELLED, QueueStatus.PAUSED}:
                self._queue = queue
                return False
            item.status, item.progress, item.error = QueueStatus.QUEUED, 0, None
            self._write_queue_locked(queue)
            self._queue = queue
            return True

    def due_count(self) -> int:
        now = _local_now()
        with self._lock, self._process_lock():
            queue = self._read_queue_locked()
            self._queue = queue
            return sum(
                1
                for item in queue
                if item.status == QueueStatus.QUEUED
                or (item.status == QueueStatus.SCHEDULED and item.scheduled_at and item.scheduled_at <= now)
            )

    def remove(self, item_id: str) -> bool:
        with self._lock, self._process_lock():
            queue = self._read_queue_locked()
            for index, item in enumerate(queue):
                if item.id == item_id:
                    del queue[index]
                    self._write_queue_locked(queue)
                    self._queue = queue
                    return True
            self._queue = queue
            return False

    def move(self, item_id: str, offset: int) -> bool:
        with self._lock, self._process_lock():
            queue = self._read_queue_locked()
            items = list(queue)
            index = next((i for i, item in enumerate(items) if item.id == item_id), -1)
            if index < 0:
                self._queue = queue
                return False
            new_index = max(0, min(len(items) - 1, index + offset))
            items.insert(new_index, items.pop(index))
            queue = deque(items)
            self._write_queue_locked(queue)
            self._queue = queue
            return True

    def get(self, item_id: str) -> QueueItem | None:
        with self._lock, self._process_lock():
            queue = self._read_queue_locked()
            self._queue = queue
            return next((item for item in queue if item.id == item_id), None)

    def list_items(self) -> list[QueueItem]:
        with self._lock, self._process_lock():
            queue = self._read_queue_locked()
            self._queue = queue
            return list(queue)

    def clear(self) -> None:
        with self._lock, self._process_lock():
            queue: deque[QueueItem] = deque()
            self._write_queue_locked(queue)
            self._queue = queue
