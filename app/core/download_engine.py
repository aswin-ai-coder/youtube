from __future__ import annotations

from typing import Any

from yt_dlp import YoutubeDL

from app.core.models import DownloadKind, DownloadOptions


class DownloadEngine:
    """UI-independent yt-dlp engine shared by desktop and Android."""

    def build_format(self, options: DownloadOptions) -> str:
        if options.kind == DownloadKind.AUDIO:
            return "bestaudio/best"

        height = self._height(options.quality)
        height_filter = f"[height<={height}]" if height else ""
        codec_filter = "[vcodec*=avc1]" if options.video_codec == "h264" else ""

        if options.kind == DownloadKind.VIDEO:
            preferred = f"bestvideo{height_filter}{codec_filter}"
            return f"{preferred}/bestvideo{height_filter}{codec_filter}/best"

        audio_filter = "[acodec*=mp4a]" if options.audio_codec in {"aac", "m4a"} else ""
        preferred = f"bestvideo{height_filter}{codec_filter}+bestaudio{audio_filter}"
        fallback = f"bestvideo{height_filter}{codec_filter}+bestaudio/best{height_filter}/best"
        return f"{preferred}/{fallback}"

    def build_options(self, options: DownloadOptions, progress_hook: Any | None = None) -> dict[str, Any]:
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
            ydl_options["subtitleslangs"] = options.subtitle_languages or ([options.translation_language] if options.translate_subtitles else ["en"])
            ydl_options["subtitlesformat"] = options.subtitle_format
        if options.translate_subtitles:
            ydl_options["translate_subtitles"] = True
            ydl_options["subtitleslangs"] = [options.translation_language]
        return ydl_options

    def download(self, options: DownloadOptions, progress_hook: Any | None = None) -> str | None:
        """Download media and return the most recently finalized output path."""
        options.output_dir.mkdir(parents=True, exist_ok=True)
        final_path: str | None = None

        def hook(data: dict[str, Any]) -> None:
            nonlocal final_path
            filename = data.get("filename") or data.get("filepath")
            if filename:
                final_path = str(filename)
            if progress_hook:
                progress_hook(data)

        def postprocessor_hook(data: dict[str, Any]) -> None:
            nonlocal final_path
            info = data.get("info_dict") or {}
            filename = info.get("filepath") or data.get("filepath")
            if filename:
                final_path = str(filename)

        ydl_options = self.build_options(options, hook)
        ydl_options["postprocessor_hooks"] = [postprocessor_hook]

        with YoutubeDL(ydl_options) as ydl:
            ydl.download([options.url])

        if final_path:
            return final_path
        return None

    def _postprocessors(self, options: DownloadOptions) -> list[dict[str, Any]]:
        processors: list[dict[str, Any]] = []
        if options.kind == DownloadKind.AUDIO:
            processors.append({"key": "FFmpegExtractAudio", "preferredcodec": options.audio_codec, "preferredquality": options.audio_bitrate})
        if options.embed_metadata:
            processors.append({"key": "FFmpegMetadata"})
        if options.embed_thumbnail and options.kind == DownloadKind.AUDIO:
            processors.append({"key": "EmbedThumbnail"})
        if options.embed_subtitles:
            processors.append({"key": "FFmpegEmbedSubtitle"})
        return processors

    @staticmethod
    def _height(quality: str) -> int | None:
        if not quality or quality == "Best":
            return None
        try:
            return int(quality.removesuffix("p"))
        except ValueError:
            return None
