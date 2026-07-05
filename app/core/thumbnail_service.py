from __future__ import annotations

from hashlib import sha256
from pathlib import Path

import requests


class ThumbnailService:
    """Download and cache thumbnails for previews and history."""

    def __init__(self, cache_dir: str | Path | None = None) -> None:
        self.cache_dir = Path(cache_dir or Path.home() / ".youtube_downloader" / "thumbs")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def cached_path(self, url: str) -> Path:
        digest = sha256(url.encode("utf-8")).hexdigest()
        suffix = Path(url.split("?")[0]).suffix.lower()
        if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
            suffix = ".jpg"
        return self.cache_dir / f"{digest}{suffix}"

    def fetch(self, url: str) -> Path | None:
        if not url:
            return None
        target = self.cached_path(url)
        if target.exists() and target.stat().st_size > 0:
            return target
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        target.write_bytes(response.content)
        return target

    def clear(self) -> None:
        for item in self.cache_dir.glob("*"):
            if item.is_file():
                item.unlink()
