from kivy.metrics import dp

from kivymd.uix.boxlayout import MDBoxLayout
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
        from kivy.app import App

        app = App.get_running_app()
        if not hasattr(app, "sm") or "home" not in app.sm.screen_names:
            return

        home = app.sm.get_screen("home")
        coordinator = getattr(home, "coordinator", None)
        if coordinator is None:
            return

        for item in home.queue.list_items():
            if item.id in self.cards:
                card = self.cards[item.id]
            else:
                card = self.add_download(
                    item.id,
                    item.title or "Download",
                    {
                        "pause": coordinator.pause,
                        "resume": coordinator.resume,
                        "cancel": coordinator.cancel,
                    },
                )

            card.update_progress(item.progress)
            if item.status.value == "queued":
                card.update_status("Queued")
            elif item.status.value == "running":
                card.update_status("Downloading")
            elif item.status.value == "paused":
                card.update_status("Paused")
            elif item.status.value == "completed":
                card.update_status("Completed")
            elif item.status.value == "failed":
                card.update_status("Failed")
            elif item.status.value == "cancelled":
                card.update_status("Cancelled")

    def add_download(self, item_id, title, callbacks):
        existing = self.cards.get(item_id)
        if existing is not None:
            return existing

        card = QueueItemCard(item_id, title, callbacks)
        self.cards[item_id] = card
        self.container.add_widget(card)
        return card
