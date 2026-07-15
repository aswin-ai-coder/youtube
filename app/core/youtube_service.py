from __future__ import annotations

from typing import Any

from app.core.ytdlp_factory import create_ytdlp

from app.core.models import MediaFormat, SubtitleTrack, VideoMetadata


class YouTubeService:
    """Fetch lightweight metadata for a YouTube URL using yt-dlp."""

    def get_video_info(self, url: str) -> VideoMetadata:
        opts = {
            "quiet": True,
            "skip_download": True,
            "no_warnings": True,
            "extract_flat": False,
        }

        with create_ytdlp(opts) as ydl:
            info = ydl.extract_info(url, download=False)

        if not isinstance(info, dict):
            return VideoMetadata()

        return self._metadata_from_info(info)

    def _metadata_from_info(self, info: dict[str, Any]) -> VideoMetadata:
        formats = self._extract_formats(info.get("formats") or [])
        qualities = self._extract_qualities(formats)
        subtitles = self._extract_subtitles(info.get("subtitles") or {}, False)
        automatic = self._extract_subtitles(info.get("automatic_captions") or {}, True)
        fps_values = sorted(
            {fmt.fps for fmt in formats if fmt.fps is not None}, reverse=True
        )
        video_codecs = sorted({fmt.vcodec for fmt in formats if fmt.vcodec})
        audio_codecs = sorted({fmt.acodec for fmt in formats if fmt.acodec})

        best_video = self._best_video_format(formats)
        best_audio = self._best_audio_format(formats)
        return VideoMetadata(
            title=info.get("title"),
            channel=info.get("uploader") or info.get("channel"),
            duration=info.get("duration"),
            views=info.get("view_count"),
            upload_date=info.get("upload_date"),
            thumbnail=info.get("thumbnail"),
            qualities=qualities,
            description=info.get("description"),
            video_id=info.get("id"),
            webpage_url=info.get("webpage_url"),
            playlist_count=info.get("playlist_count"),
            is_live=bool(info.get("is_live")),
            was_live=bool(info.get("was_live")),
            fps_values=fps_values,
            video_codecs=video_codecs,
            audio_codecs=audio_codecs,
            formats=formats,
            subtitles=[*subtitles, *automatic],
            chapters=info.get("chapters") or [],
            comment_count=info.get("comment_count"),
            best_resolution=best_video.resolution if best_video else None,
            best_video_codec=best_video.vcodec if best_video else None,
            best_fps=best_video.fps if best_video else None,
            best_audio_codec=best_audio.acodec if best_audio else None,
            best_bitrate=(
                best_video.bitrate
                if best_video
                else best_audio.bitrate if best_audio else None
            ),
            is_hdr=any(fmt.hdr for fmt in formats),
        )

    def _best_video_format(self, formats: list[MediaFormat]) -> MediaFormat | None:
        video_formats = [fmt for fmt in formats if fmt.height is not None]
        if not video_formats:
            return None
        return max(
            video_formats,
            key=lambda fmt: (
                fmt.height or 0,
                fmt.fps or 0,
                fmt.bitrate or 0,
            ),
        )

    def _best_audio_format(self, formats: list[MediaFormat]) -> MediaFormat | None:
        audio_formats = [fmt for fmt in formats if fmt.acodec]
        if not audio_formats:
            return None
        return max(
            audio_formats,
            key=lambda fmt: (
                fmt.bitrate or 0,
                fmt.filesize or 0,
            ),
        )

    def _extract_qualities(self, formats: list[MediaFormat]) -> list[str]:
        seen: set[str] = set()
        qualities: list[str] = []
        for fmt in formats:
            if fmt.height:
                quality = f"{fmt.height}p"
                if quality not in seen:
                    seen.add(quality)
                    qualities.append(quality)
        qualities.sort(key=lambda x: int(x[:-1]), reverse=True)
        return qualities

    def _extract_formats(self, raw_formats: list[dict[str, Any]]) -> list[MediaFormat]:
        formats: list[MediaFormat] = []
        for fmt in raw_formats:
            dynamic_range = str(fmt.get("dynamic_range") or "").lower()
            formats.append(
                MediaFormat(
                    format_id=str(fmt.get("format_id") or ""),
                    ext=fmt.get("ext"),
                    resolution=fmt.get("resolution"),
                    height=fmt.get("height"),
                    fps=fmt.get("fps"),
                    vcodec=self._none_codec(fmt.get("vcodec")),
                    acodec=self._none_codec(fmt.get("acodec")),
                    bitrate=fmt.get("tbr") or fmt.get("abr") or fmt.get("vbr"),
                    filesize=fmt.get("filesize") or fmt.get("filesize_approx"),
                    hdr="hdr" in dynamic_range,
                )
            )
        return formats

    def _extract_subtitles(
        self, raw_subtitles: dict[str, list[dict[str, Any]]], automatic: bool
    ) -> list[SubtitleTrack]:
        tracks: list[SubtitleTrack] = []
        for language, formats in raw_subtitles.items():
            tracks.append(
                SubtitleTrack(
                    language=language,
                    name=formats[0].get("name") if formats else None,
                    automatic=automatic,
                    formats=tuple(
                        sorted(
                            {
                                str(item.get("ext"))
                                for item in formats
                                if item.get("ext")
                            }
                        )
                    ),
                )
            )
        return tracks

    def _none_codec(self, value: Any) -> str | None:
        if not value or value == "none":
            return None
        return str(value)
