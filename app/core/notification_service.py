from __future__ import annotations

try:
    from plyer import notification
except ImportError:
    notification = None


class NotificationService:
    """Small cross-platform notification facade."""

    @staticmethod
    def show(title: str, message: str) -> None:
        if notification is None:
            return
        try:
            notification.notify(title=title, message=message, timeout=5)
        except Exception:
            return

    def notify(self, title: str, message: str) -> None:
        """Compatibility method for background-service callers."""
        self.show(title, message)
