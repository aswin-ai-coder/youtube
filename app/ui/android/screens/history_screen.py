from __future__ import annotations

from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView

from app.core.history_service import HistoryService


class HistoryScreen(MDScreen):
    """Display the same persistent history written by the download service."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.history = HistoryService()
        scroll = MDScrollView()
        self.container = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing=dp(12),
            padding=dp(16),
        )
        scroll.add_widget(self.container)
        self.add_widget(scroll)

    def on_pre_enter(self, *_args):
        self.refresh()

    def refresh(self, *_args):
        self.container.clear_widgets()
        records = self.history.list_recent(limit=100)
        if not records:
            self.container.add_widget(
                MDLabel(text="No downloads yet", halign="center", adaptive_height=True)
            )
            return
        for record in records:
            self.add_history(record)

    def add_history(self, record):
        if isinstance(record, str):
            title, status, date, url = record, "completed", "", ""
        else:
            title = record.get("title") or "Untitled"
            status = record.get("status") or "unknown"
            date = record.get("date") or ""
            url = record.get("url") or ""

        card = MDCard(
            orientation="vertical",
            adaptive_height=True,
            padding=dp(16),
            spacing=dp(6),
            radius=[18],
        )
        card.add_widget(MDLabel(text=title, bold=True, adaptive_height=True))
        card.add_widget(MDLabel(text=f"Status: {status}", adaptive_height=True))
        if date:
            card.add_widget(MDLabel(text=date, adaptive_height=True))
        if url:
            card.add_widget(MDLabel(text=url, adaptive_height=True, max_lines=2))
        self.container.add_widget(card)
