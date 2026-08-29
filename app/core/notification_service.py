from __future__ import annotations

try:
    from plyer import notification
except ImportError:
    notification = None


class NotificationService:
    @staticmethod
    def show(title: str, message: str) -> None:
        if notification is None:
            return
        try:
            notification.notify(title=title, message=message, timeout=5)
        except Exception:
            return
