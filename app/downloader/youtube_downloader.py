from __future__ import annotations

from pathlib import Path

from app.core.download_service import DownloadService
from app.core.history_service import HistoryService
from app.core.models import DownloadOptions, SubtitleTrack, VideoMetadata
from app.core.playlist_service import PlaylistMetadata, PlaylistService
from app.core.settings_service import SettingsService
from app.core.subtitle_service import SubtitleService
from app.core.thumbnail_service import ThumbnailService
from app.core.youtube_service import YouTubeService


class YouTubeDownloader:
    """High-level facade for shared downloader services."""

    def __init__(self) -> None:
        self.settings = SettingsService()
        self.history = HistoryService()
        self.youtube = YouTubeService()
        self.playlist = PlaylistService()
        self.subtitle = SubtitleService()
        self.thumbnail = ThumbnailService()
        self.download = DownloadService()

    def analyze(self, url: str) -> VideoMetadata:
        return self.youtube.get_video_info(url)

    def playlist_info(self, url: str) -> PlaylistMetadata:
        return self.playlist.get_playlist_info(url)

    def list_subtitles(self, url: str) -> list[SubtitleTrack]:
        return self.youtube.get_video_info(url).subtitles

    def download_media(self, options: DownloadOptions, progress_hook=None) -> None:
        self.download.download(options, progress_hook)

    def download_subtitles(self, url: str, output_dir: str | Path, languages: list[str] | None = None) -> str:
        return self.subtitle.download_subtitles(url, output_dir, languages)

    def fetch_thumbnail(self, url: str) -> Path | None:
        return self.thumbnail.fetch(url)

    def record_history(self, *, title: str, url: str, duration: int | None = None, size_bytes: int | None = None, output_path: str | None = None, thumbnail_url: str | None = None, status: str = "completed") -> None:
        self.history.add_record(title=title, url=url, duration=duration, size_bytes=size_bytes, output_path=output_path, thumbnail_url=thumbnail_url, status=status)

    def save_settings(self, values: dict[str, object]) -> None:
        self.settings.update(values)
        self.settings.save()

    def load_settings(self) -> dict[str, object]:
        return self.settings.as_dict()
