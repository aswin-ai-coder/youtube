from __future__ import annotations

from dataclasses import dataclass

import requests
from yt_dlp.version import __version__ as yt_dlp_version


@dataclass(slots=True, frozen=True)
class UpdateStatus:
    current_version: str
    latest_version: str
    update_available: bool
    package_url: str


class UpdateService:
    """Check PyPI for newer yt-dlp releases used by the downloader engine."""

    def check(self) -> UpdateStatus:
        url = "https://pypi.org/pypi/yt-dlp/json"
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        latest = str(response.json()["info"]["version"])
        return UpdateStatus(
            current_version=yt_dlp_version,
            latest_version=latest,
            update_available=self._version_tuple(latest) > self._version_tuple(yt_dlp_version),
            package_url="https://pypi.org/project/yt-dlp/",
        )

    def _version_tuple(self, value: str) -> tuple[int, ...]:
        parts: list[int] = []
        for piece in value.replace("-", ".").split("."):
            if piece.isdigit():
                parts.append(int(piece))
        return tuple(parts)
