from __future__ import annotations

from pathlib import Path

from kivy.utils import platform


class AndroidStorageService:
    """Return an Android-safe app-owned Downloads directory."""

    @staticmethod
    def default_download_folder() -> str:
        fallback = Path.home() / "Downloads" / "YouTube Downloader"
        if platform != "android":
            fallback.mkdir(parents=True, exist_ok=True)
            return str(fallback)

        try:
            from jnius import autoclass

            Environment = autoclass("android.os.Environment")
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            base = PythonActivity.mActivity.getExternalFilesDir(
                Environment.DIRECTORY_DOWNLOADS
            )
            if base is not None:
                folder = Path(str(base)) / "YouTube Downloader"
                folder.mkdir(parents=True, exist_ok=True)
                return str(folder)
        except Exception:
            pass

        fallback.mkdir(parents=True, exist_ok=True)
        return str(fallback)

    @classmethod
    def resolve_download_folder(cls, configured: str | None) -> str:
        if configured:
            path = Path(configured).expanduser()
            try:
                path.mkdir(parents=True, exist_ok=True)
                if path.is_dir() and path != Path.home() / "Downloads" / "YouTube Downloader":
                    return str(path)
            except OSError:
                pass
        return cls.default_download_folder()
