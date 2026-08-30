from kivy.metrics import dp
from kivy.app import App

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView

from app.ui.android.widgets.queue_item import QueueItem as QueueItemCard


class QueueScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cards = {}

        scroll = MDScrollView()
        self.container = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing=dp(12),
            padding=dp(16),
        )
        scroll.add_widget(self.container)
        self.add_widget(scroll)

    def on_pre_enter(self):
        app = App.get_running_app()
        if not hasattr(app, "sm") or "home" not in app.sm.screen_names:
            return

        home = app.sm.get_screen("home")
        coordinator = getattr(home, "coordinator", None)
        if coordinator is None:
            return

        for item in home.queue.list_items():
            card = self.cards.get(item.id)
            if card is None:
                card = self.add_download(
                    item.id,
                    item.title or "Download",
                    {
                        "pause": coordinator.pause,
                        "resume": coordinator.resume,
                        "cancel": coordinator.cancel,
                    },
                )

            home.queue_cards[item.id] = card
            card.update_progress(item.progress)
            card.update_status(self._status_text(item.status.value))
            card.update_speed(item.speed_text or "--")
            downloaded = self._format_size(item.downloaded_bytes)
            total = self._format_size(item.total_bytes) if item.total_bytes else "--"
            card.update_size(downloaded, total)
            card.update_eta("--" if item.eta_seconds is None else f"{item.eta_seconds}s")

    def add_download(self, item_id, title, callbacks):
        existing = self.cards.get(item_id)
        if existing is not None:
            return existing

        card = QueueItemCard(item_id, title, callbacks)
        self.cards[item_id] = card
        self.container.add_widget(card)
        return card

    @staticmethod
    def _status_text(status: str) -> str:
        return {
            "queued": "Queued",
            "scheduled": "Scheduled",
            "running": "Downloading",
            "paused": "Paused",
            "completed": "Completed",
            "failed": "Failed",
            "cancelled": "Cancelled",
        }.get(status, status.title())

    @staticmethod
    def _format_size(value: int) -> str:
        if value <= 0:
            return "0 B"
        size = float(value)
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if size < 1024 or unit == "TB":
                return f"{int(size)} B" if unit == "B" else f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
