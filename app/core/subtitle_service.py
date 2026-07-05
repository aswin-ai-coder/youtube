from __future__ import annotations

from pathlib import Path

from yt_dlp import YoutubeDL


class SubtitleService:
    """Download subtitles for a video using yt-dlp."""

    def list_subtitles(self, url: str) -> list[str]:
        options = {
            "quiet": True,
            "skip_download": True,
            "writesubtitles": True,
            "list_subtitles": True,
        }
        with YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
        subtitles = info.get("subtitles") or {}
        return sorted(subtitles.keys())

    def download_subtitles(
        self,
        url: str,
        output_dir: str | Path,
        languages: list[str] | None = None,
        translate: bool = False,
        translation_language: str = "en",
        subtitle_format: str = "srt",
    ) -> str:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        options = {
            "quiet": True,
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": languages or [translation_language],
            "subtitlesformat": subtitle_format,
            "outtmpl": str(output_path / "%(title)s.%(ext)s"),
        }
        if translate:
            options["translate_subtitles"] = True
            options["subtitleslangs"] = [translation_language]
        with YoutubeDL(options) as ydl:
            ydl.download([url])
        return str(output_path)
