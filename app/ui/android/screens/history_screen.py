from kivy.metrics import dp

from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel


class HistoryScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        scroll = MDScrollView()

        self.container = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing=dp(12),
            padding=dp(16),
        )

        scroll.add_widget(self.container)

        self.add_widget(scroll)

    def add_history(self, title):

        card = MDCard(
            orientation="vertical",
            adaptive_height=True,
            padding=dp(16),
            radius=[18],
        )

        card.add_widget(

            MDLabel(
                text=title,
                adaptive_height=True,
            )

        )

        self.container.add_widget(card)
