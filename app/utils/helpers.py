from PySide6.QtGui import QPixmap

from app.core.thumbnail_service import ThumbnailService


def download_thumbnail(url: str) -> QPixmap | None:

    if not url:
        return None

    path = ThumbnailService().fetch(url)
    if not path:
        return None

    pixmap = QPixmap()
    pixmap.load(str(path))
    return pixmap


def format_duration(seconds: int | None) -> str:
    if not seconds:
        return "-"
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:d}:{secs:02d}"


def format_number(value: int | None) -> str:
    if value is None:
        return "-"
    return f"{value:,}"
