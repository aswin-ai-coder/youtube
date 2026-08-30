from __future__ import annotations

from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView

from app.core.models import QueueStatus
from app.core.queue_service import QueueService
from app.ui.android.widgets.queue_item import QueueItem as QueueItemCard


class QueueScreen(MDScreen):
    """Live view of the persistent queue shared with the Android service."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.queue = QueueService()
        self.cards = {}
        self._last_signature = None

        scroll = MDScrollView()
        self.container = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing=dp(12),
            padding=dp(16),
        )
        scroll.add_widget(self.container)
        self.add_widget(scroll)
        self._refresh_event = Clock.schedule_interval(self.refresh, 0.75)
        Clock.schedule_once(self.refresh, 0)

    def refresh(self, *_args):
        items = self.queue.list_items()
        signature = tuple((item.id, item.title, item.status.value, item.progress, item.error) for item in items)
        if signature == self._last_signature:
            return
        self._last_signature = signature

        existing = set(self.cards)
        for item in items:
            card = self.cards.get(item.id)
            if card is None:
                card = self.add_download(item.id, item.title or item.url, {
                    "pause": self.pause,
                    "resume": self.resume,
                    "cancel": self.cancel,
                    "retry": self.retry,
                    "remove": self.remove,
                })
            card.update_progress(item.progress)
            status = item.status.value.replace("_", " ").title()
            if item.error:
                status = f"Failed: {item.error}"
            card.update_status(status)
            existing.discard(item.id)

        for item_id in existing:
            card = self.cards.pop(item_id)
            self.container.remove_widget(card)

    def add_download(self, item_id, title, callbacks):
        card = QueueItemCard(item_id, title, callbacks)
        self.cards[item_id] = card
        self.container.add_widget(card)
        return card

    def pause(self, item_id):
        item = self.queue.get(item_id)
        if item and item.status in {QueueStatus.QUEUED, QueueStatus.SCHEDULED, QueueStatus.RUNNING}:
            self.queue.update(item_id, status=QueueStatus.PAUSED)
            self.refresh()

    def resume(self, item_id):
        item = self.queue.get(item_id)
        if item and item.status == QueueStatus.PAUSED:
            self.queue.update(item_id, status=QueueStatus.QUEUED, progress=0, error=None)
            self.refresh()

    def cancel(self, item_id):
        item = self.queue.get(item_id)
        if item and item.status not in {QueueStatus.COMPLETED, QueueStatus.CANCELLED}:
            self.queue.update(item_id, status=QueueStatus.CANCELLED)
            self.refresh()

    def retry(self, item_id):
        if self.queue.retry(item_id):
            self.refresh()

    def remove(self, item_id):
        item = self.queue.get(item_id)
        if item and item.status not in {QueueStatus.RUNNING}:
            self.queue.remove(item_id)
            self.refresh()

    def on_leave(self, *_args):
        # Keep the persistent service running; only stop this UI poller.
        if self._refresh_event is not None:
            self._refresh_event.cancel()
            self._refresh_event = None

    def on_enter(self, *_args):
        if self._refresh_event is None:
            self._refresh_event = Clock.schedule_interval(self.refresh, 0.75)
        self.refresh()
