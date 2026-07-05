from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from yt_dlp import YoutubeDL


@dataclass(slots=True)
class PlaylistMetadata:
    title: str | None = None
    count: int | None = None
    is_playlist: bool = False
    entries: list[dict[str, Any]] | None = None


class PlaylistService:
    """Inspect YouTube playlists and provide basic metadata."""

    def get_playlist_info(self, url: str) -> PlaylistMetadata:
        options = {
            "quiet": True,
            "skip_download": True,
            "extract_flat": True,
            "noplaylist": False,
        }
        with YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
        if isinstance(info, dict):
            entries = info.get("entries") or []
            return PlaylistMetadata(
                title=info.get("title"),
                count=len([entry for entry in entries if isinstance(entry, dict)]),
                is_playlist=bool(
                    info.get("_type") == "playlist" or info.get("entries")
                ),
                entries=[
                    {
                        "index": index,
                        "title": entry.get("title") or f"Video {index}",
                        "url": entry.get("url") or entry.get("id"),
                        "id": entry.get("id"),
                    }
                    for index, entry in enumerate(entries, start=1)
                    if isinstance(entry, dict)
                ],
            )
        return PlaylistMetadata()
