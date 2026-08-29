from __future__ import annotations

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.widget import Widget

from app.core.favorites_service import FavoritesService
from app.ui.mobile.state import mobile_manager
from app.core.queue_service import QueueItem
from app.core.models import DownloadKind
from app.core.settings_service import SettingsService


class FavoritesPage(TabbedPanelItem):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.favorites = FavoritesService()
        self.settings = SettingsService()
        self.list_layout = BoxLayout(orientation="vertical", spacing=8, size_hint_y=None)
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))
        self.content = self._build()
        self.refresh()

    def _build(self) -> BoxLayout:
        layout = BoxLayout(orientation="vertical", padding=12, spacing=8)
        refresh_btn = Button(text="Refresh", size_hint_y=None, height=48)
        refresh_btn.bind(on_press=lambda *_args: self.refresh())
        clear_btn = Button(text="Clear Favorites", size_hint_y=None, height=48)
        clear_btn.bind(on_press=lambda *_args: self.clear())
        scroll = ScrollView()
        scroll.add_widget(self.list_layout)
        layout.add_widget(refresh_btn)
        layout.add_widget(clear_btn)
        layout.add_widget(scroll)
        return layout

    def refresh(self) -> None:
        self.list_layout.clear_widgets()
        rows = self.favorites.all()
        if not rows:
            self.list_layout.add_widget(Label(text="No favorites yet", size_hint_y=None, height=48))
            return
        for url, title, thumbnail in rows:
            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=92, spacing=8)
            row.add_widget(AsyncImage(source=thumbnail or "", size_hint_x=None, width=140))
            row.add_widget(Label(text=title or url, size_hint_x=0.6, text_size=(None, None)))
            actions = BoxLayout(orientation="vertical", size_hint_x=0.25, spacing=4)
            download = Button(text="Download")
            download.bind(on_press=lambda _btn, u=url, t=title, th=thumbnail: self._download(u, t, th))
            remove = Button(text="Remove")
            remove.bind(on_press=lambda _btn, u=url: self._remove(u))
            actions.add_widget(download)
            actions.add_widget(remove)
            row.add_widget(actions)
            self.list_layout.add_widget(row)
        self.list_layout.add_widget(Widget(size_hint_y=None, height=8))

    def _download(self, url: str, title: str, thumbnail: str) -> None:
        mobile_manager.enqueue(
            QueueItem(
                url=url,
                output_dir=self.settings.get("download_folder"),
                kind=DownloadKind.VIDEO_AUDIO,
                quality="Best",
                audio_codec="mp3",
                audio_bitrate="320",
                video_codec="h264",
                container="mp4",
                filename_template=self.settings.get("filename_template", "%(title)s.%(ext)s"),
                embed_thumbnail=True,
                embed_metadata=True,
                title=title or url,
                thumbnail_url=thumbnail or None,
            )
        )

    def _remove(self, url: str) -> None:
        self.favorites.remove(url)
        self.refresh()

    def clear(self) -> None:
        for url, _title, _thumbnail in self.favorites.all():
            self.favorites.remove(url)
        self.refresh()
