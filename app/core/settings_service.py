import json
from pathlib import Path
from typing import Any


DEFAULT_SETTINGS: dict[str, Any] = {
    "theme": "dark",
    "accent_color": "#2563eb",
    "language": "en",
    "download_folder": str(Path.home() / "Downloads" / "YouTube Downloader"),
    "filename_template": "%(title)s.%(ext)s",
    "concurrent_downloads": 2,
    "max_retries": 10,
    "concurrent_fragments": 4,
    "ffmpeg_path": "",
    "update_channel": "stable",
    "notifications": True,
    "clipboard_monitoring": True,
    "window_geometry": "",
    "splitter_sizes": [],
}


class SettingsService:
    """Persist user settings as a simple JSON file."""

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path or Path.home() / ".youtube_downloader_settings.json")
        self._data: dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        self._data = DEFAULT_SETTINGS.copy()
        if self.path.exists():
            try:
                loaded = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    self._data.update(loaded)
            except (json.JSONDecodeError, OSError):
                self._data = DEFAULT_SETTINGS.copy()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix(self.path.suffix + ".tmp")
        temp.write_text(
            json.dumps(self._data, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        temp.replace(self.path)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def update(self, values: dict[str, Any]) -> None:
        self._data.update(values)

    def as_dict(self) -> dict[str, Any]:
        return self._data.copy()
