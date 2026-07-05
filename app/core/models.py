from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any


class DownloadKind(StrEnum):
    VIDEO = "video"
    AUDIO = "audio"
    VIDEO_AUDIO = "video_audio"


class QueueStatus(StrEnum):
    QUEUED = "queued"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(slots=True, frozen=True)
class MediaFormat:
    format_id: str
    ext: str | None = None
    resolution: str | None = None
    height: int | None = None
    fps: float | None = None
    vcodec: str | None = None
    acodec: str | None = None
    bitrate: float | None = None
    filesize: int | None = None
    hdr: bool = False


@dataclass(slots=True, frozen=True)
class SubtitleTrack:
    language: str
    name: str | None = None
    automatic: bool = False
    formats: tuple[str, ...] = ()


@dataclass(slots=True)
class VideoMetadata:
    title: str | None = None
    channel: str | None = None
    duration: int | None = None
    views: int | None = None
    upload_date: str | None = None
    thumbnail: str | None = None
    qualities: list[str] = field(default_factory=list)
    description: str | None = None
    video_id: str | None = None
    webpage_url: str | None = None
    playlist_count: int | None = None
    is_live: bool = False
    was_live: bool = False
    fps_values: list[float] = field(default_factory=list)
    video_codecs: list[str] = field(default_factory=list)
    audio_codecs: list[str] = field(default_factory=list)
    formats: list[MediaFormat] = field(default_factory=list)
    subtitles: list[SubtitleTrack] = field(default_factory=list)
    chapters: list[dict[str, Any]] = field(default_factory=list)
    comment_count: int | None = None
    best_resolution: str | None = None
    best_video_codec: str | None = None
    best_audio_codec: str | None = None
    best_fps: float | None = None
    best_bitrate: float | None = None
    is_hdr: bool = False


@dataclass(slots=True)
class DownloadOptions:
    url: str
    output_dir: Path
    kind: DownloadKind = DownloadKind.VIDEO_AUDIO
    quality: str = "Best"
    audio_bitrate: str = "320"
    audio_codec: str = "mp3"
    video_codec: str = "h264"
    container: str = "mp4"
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
    playlist: bool = False
    playlist_items: list[str] = field(default_factory=list)
    max_retries: int = 10
    concurrent_fragments: int = 4
    ffmpeg_path: str | None = None

    @property
    def audio_only(self) -> bool:
        return self.kind == DownloadKind.AUDIO
