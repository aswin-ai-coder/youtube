from __future__ import annotations

from typing import Any

from PySide6.QtCore import QThread, Signal

from app.core.download_engine import DownloadEngine
from app.core.models import DownloadKind, DownloadOptions
from app.utils.error_handler import ErrorHandler


class DownloadService(DownloadEngine):
    """Desktop-compatible facade over the shared yt-dlp engine."""


class DownloadWorker(QThread):
    progress = Signal(int)
    status = Signal(str)
    speed = Signal(str)
    eta = Signal(str)
    size = Signal(str, str)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, *, options: DownloadOptions | None = None, url: str = "", output_dir: str = "", audio_only: bool = False, quality: str = "Best", audio_codec: str = "mp3", audio_bitrate: str = "320", container: str = "mp4", filename_template: str = "%(title)s.%(ext)s") -> None:
        super().__init__()
        self.options = options or DownloadOptions(
            url=url,
            output_dir=__import__("pathlib").Path(output_dir),
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
            downloaded = data.get("downloaded_bytes", 0) or 0
            total = data.get("total_bytes") or data.get("total_bytes_estimate") or 0
            if total > 0:
                self.progress.emit(min(100, int(downloaded * 100 / total)))
            speed = data.get("speed") or 0
            eta = data.get("eta") or 0
            self.speed.emit(f"{speed / 1024 / 1024:.2f} MB/s" if speed else "--")
            self.size.emit(f"{downloaded / 1024 / 1024:.1f} MB", f"{total / 1024 / 1024:.1f} MB" if total else "--")
            self.eta.emit(f"{eta}s" if eta else "--")
            self.status.emit("Downloading")
        elif status == "finished":
            self.output_file = data.get("filename") or self.output_file
            self.status.emit("Finalizing...")

    def build_format(self) -> str:
        return self.service.build_format(self.options)

    def run(self) -> None:
        try:
            self.service.download(self.options, self.hook)
            self.progress.emit(100)
            self.status.emit("Finished")
            self.finished.emit(self.output_file or str(self.options.output_dir))
        except Exception as exc:
            self.error.emit(ErrorHandler.handle(exc, context="DownloadWorker"))

    def stop(self) -> None:
        self.cancelled = True
