from __future__ import annotations

from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView

from app.core.favorites_service import FavoritesService


class FavoritesScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = FavoritesService()
        scroll = MDScrollView()
        self.container = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing=dp(12), padding=dp(16))
        scroll.add_widget(self.container)
        self.add_widget(scroll)

    def on_pre_enter(self, *_args):
        self.refresh()

    def refresh(self, *_args):
        self.container.clear_widgets()
        favorites = self.service.all()
        if not favorites:
            self.container.add_widget(MDLabel(text="No favorites yet", halign="center", adaptive_height=True))
            return
        for url, title, thumbnail in favorites:
            card = MDCard(orientation="vertical", adaptive_height=True, padding=dp(16), spacing=dp(8), radius=[18])
            card.add_widget(MDLabel(text=title or "Untitled", bold=True, adaptive_height=True))
            card.add_widget(MDLabel(text=url, adaptive_height=True, max_lines=2))
            remove = MDButton(style="outlined")
            remove.add_widget(MDButtonText(text="REMOVE"))
            remove.bind(on_release=lambda *_args, u=url: self.remove(u))
            card.add_widget(remove)
            self.container.add_widget(card)

    def remove(self, url: str):
        self.service.remove(url)
        self.refresh()
