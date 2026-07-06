from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import QThread, Signal
from yt_dlp import YoutubeDL

from app.core.models import DownloadKind, DownloadOptions


class DownloadService:
    """Build and run yt-dlp downloads from shared backend options."""

    def build_format(self, options: DownloadOptions) -> str:
        if options.kind == DownloadKind.AUDIO:
            return "bestaudio/best"

        height = self._height(options.quality)
        height_filter = f"[height<={height}]" if height else ""
        codec_filter = "[vcodec*=avc1]" if options.video_codec == "h264" else ""

        if options.kind == DownloadKind.VIDEO:
            preferred = f"bestvideo{height_filter}{codec_filter}"
            fallback = f"bestvideo{height_filter}{codec_filter}/best"
            return f"{preferred}/{fallback}"

        audio_filter = "[acodec*=mp4a]" if options.audio_codec in {"aac", "m4a"} else ""
        preferred = f"bestvideo{height_filter}{codec_filter}+bestaudio{audio_filter}"
        fallback = (
            f"bestvideo{height_filter}{codec_filter}+bestaudio/best{height_filter}/best"
        )
        return f"{preferred}/{fallback}"

    def build_options(
        self,
        options: DownloadOptions,
        progress_hook: Any | None = None,
    ) -> dict[str, Any]:
        ydl_options: dict[str, Any] = {
            "outtmpl": str(options.output_dir / options.filename_template),
            "format": self.build_format(options),
            "windowsfilenames": True,
            "continuedl": True,
            "overwrites": False,
            "retries": options.max_retries,
            "fragment_retries": options.max_retries,
            "file_access_retries": options.max_retries,
            "concurrent_fragment_downloads": options.concurrent_fragments,
            "noplaylist": not options.playlist,
            "quiet": True,
            "no_warnings": True,
            "merge_output_format": options.container,
            "postprocessors": self._postprocessors(options),
            "restrictfilenames": False,
            "trim_file_name": 240,
        }
        if options.playlist_items:
            ydl_options["playlist_items"] = ",".join(options.playlist_items)
        if options.ffmpeg_path:
            ydl_options["ffmpeg_location"] = options.ffmpeg_path
        if progress_hook:
            ydl_options["progress_hooks"] = [progress_hook]
        if options.write_subtitles:
            ydl_options["writesubtitles"] = True
        if options.write_auto_subtitles:
            ydl_options["writeautomaticsub"] = True
        if options.write_subtitles or options.write_auto_subtitles:
            ydl_options["subtitleslangs"] = options.subtitle_languages or (
                [options.translation_language]
                if options.translate_subtitles
                else ["en"]
            )
            ydl_options["subtitlesformat"] = options.subtitle_format
        if options.translate_subtitles:
            ydl_options["translate_subtitles"] = True
            ydl_options["subtitleslangs"] = [options.translation_language]
        return ydl_options

    def download(
        self,
        options: DownloadOptions,
        progress_hook: Any | None = None,
    ) -> None:
        options.output_dir.mkdir(parents=True, exist_ok=True)
        if self._output_exists(options):
            raise FileExistsError(
                f"Output already exists for template {options.filename_template}."
            )
        with YoutubeDL(self.build_options(options, progress_hook)) as ydl:
            ydl.download([options.url])

    def _output_exists(self, options: DownloadOptions) -> bool:
        pattern = options.filename_template
        if "%(ext)s" in pattern:
            pattern = pattern.replace("%(ext)s", "*")
        else:
            pattern = f"{pattern}*"
        return any(options.output_dir.glob(pattern))

    def _postprocessors(self, options: DownloadOptions) -> list[dict[str, Any]]:
        processors: list[dict[str, Any]] = []
        if options.kind == DownloadKind.AUDIO:
            processors.append(
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": options.audio_codec,
                    "preferredquality": options.audio_bitrate,
                }
            )
        if options.embed_metadata:
            processors.append({"key": "FFmpegMetadata"})
        if options.embed_thumbnail and options.kind == DownloadKind.AUDIO:
            processors.append({"key": "EmbedThumbnail"})
        if options.embed_subtitles:
            processors.append({"key": "FFmpegEmbedSubtitle"})
        return processors

    def _height(self, quality: str) -> int | None:
        if not quality or quality == "Best":
            return None
        try:
            return int(quality.removesuffix("p"))
        except ValueError:
            return None


class DownloadWorker(QThread):
    progress = Signal(int)
    status = Signal(str)
    finished = Signal(str)
    error = Signal(str)

    def __init__(
        self,
        *,
        options: DownloadOptions | None = None,
        url: str = "",
        output_dir: str | Path = "",
        audio_only: bool = False,
        quality: str = "Best",
        audio_codec: str = "mp3",
        audio_bitrate: str = "320",
        container: str = "mp4",
        filename_template: str = "%(title)s.%(ext)s",
    ) -> None:
        super().__init__()
        self.options = options or DownloadOptions(
            url=url,
            output_dir=Path(output_dir),
            kind=DownloadKind.AUDIO if audio_only else DownloadKind.VIDEO_AUDIO,
            quality=quality,
            audio_codec=audio_codec,
            audio_bitrate=audio_bitrate,
            container=container,
            filename_template=filename_template,
        )
        self.cancelled = False
        self.service = DownloadService()
        self.output_file: str | None = None

    def hook(self, data: dict[str, Any]) -> None:
        if self.cancelled:
            raise RuntimeError("Download cancelled")
        status = data.get("status")
        if status == "downloading":
            downloaded = data.get("downloaded_bytes", 0)
            total = data.get("total_bytes") or data.get("total_bytes_estimate") or 0
            if total > 0:
                self.progress.emit(int(downloaded * 100 / total))
            speed = data.get("speed")
            eta = data.get("eta")
            speed_text = f"{speed / 1024 / 1024:.2f} MB/s" if speed else ""
            eta_text = f"{eta}s" if eta else ""
            self.status.emit(f"Downloading {speed_text} ETA {eta_text}".strip())
        elif status == "finished":
            self.output_file = data.get("filename") or self.output_file
            self.status.emit("Finalizing file...")

    def build_format(self) -> str:
        return self.service.build_format(self.options)

    def run(self) -> None:
        try:
            self.service.download(self.options, self.hook)
            self.progress.emit(100)
            self.status.emit("Finished")
            output_path = self.output_file or str(self.options.output_dir)
            self.finished.emit(str(output_path))
        except Exception as exc:  # pragma: no cover - worker error path
            self.error.emit(str(exc))

    def stop(self) -> None:
        self.cancelled = True
