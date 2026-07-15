from __future__ import annotations

from typing import Any

from yt_dlp import YoutubeDL

DEFAULT_OPTIONS: dict[str, Any] = {
    "quiet": True,
    "no_warnings": True,
    "extract_flat": False,
}


def create_ytdlp(extra_options: dict[str, Any] | None = None) -> YoutubeDL:
    """
    Create a YoutubeDL instance with the project's default settings.
    """

    options = DEFAULT_OPTIONS.copy()

    if extra_options:
        options.update(extra_options)

    return YoutubeDL(options)
