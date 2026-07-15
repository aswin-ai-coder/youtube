from kivy.metrics import dp

from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout

from app.ui.android.widgets.queue_item import QueueItem


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

    def add_download(
        self,
        item_id,
        title,
        callbacks,
    ):

        card = QueueItem(
            item_id,
            title,
            callbacks,
        )

        self.cards[item_id] = card

        self.container.add_widget(card)

        return card
