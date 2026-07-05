from __future__ import annotations

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.textinput import TextInput

from core.settings_service import SettingsService


class SettingsPage(TabbedPanelItem):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.settings = SettingsService()
        self.status = Label(text="", size_hint_y=None, height=36)
        self.content = self._build()

    def _build(self) -> BoxLayout:
        layout = BoxLayout(orientation="vertical", padding=12, spacing=8)
        self.theme = Spinner(text=self.settings.get("theme"), values=["dark", "light"])
        self.accent_color = TextInput(
            text=self.settings.get("accent_color"),
            multiline=False,
            hint_text="#RRGGBB",
        )
        self.language = TextInput(
            text=self.settings.get("language"), multiline=False, hint_text="en"
        )
        self.folder = TextInput(
            text=self.settings.get("download_folder"), multiline=False
        )
        self.ffmpeg_path = TextInput(
            text=self.settings.get("ffmpeg_path"), multiline=False
        )
        self.concurrent_downloads = TextInput(
            text=str(self.settings.get("concurrent_downloads")), multiline=False
        )
        self.concurrent_fragments = TextInput(
            text=str(self.settings.get("concurrent_fragments")), multiline=False
        )
        self.retries = TextInput(
            text=str(self.settings.get("max_retries")), multiline=False
        )
        save_btn = Button(text="Save Settings", size_hint_y=None, height=48)
        save_btn.bind(on_press=self.save)
        for widget in [
            Label(text="Theme", size_hint_y=None, height=28),
            self.theme,
            Label(text="Accent color", size_hint_y=None, height=28),
            self.accent_color,
            Label(text="Language", size_hint_y=None, height=28),
            self.language,
            Label(text="Download folder", size_hint_y=None, height=28),
            self.folder,
            Label(text="FFmpeg path", size_hint_y=None, height=28),
            self.ffmpeg_path,
            Label(text="Concurrent downloads", size_hint_y=None, height=28),
            self.concurrent_downloads,
            Label(text="Concurrent fragments", size_hint_y=None, height=28),
            self.concurrent_fragments,
            Label(text="Max retries", size_hint_y=None, height=28),
            self.retries,
            save_btn,
            self.status,
        ]:
            layout.add_widget(widget)
        return layout

    def save(self, *_args) -> None:
        self.settings.update(
            {
                "theme": self.theme.text,
                "accent_color": self.accent_color.text.strip(),
                "language": self.language.text.strip(),
                "download_folder": self.folder.text.strip(),
                "ffmpeg_path": self.ffmpeg_path.text.strip(),
                "concurrent_downloads": int(self.concurrent_downloads.text or "2"),
                "concurrent_fragments": int(self.concurrent_fragments.text or "4"),
                "max_retries": int(self.retries.text or "10"),
            }
        )
        self.settings.save()
        self.status.text = "Saved"
