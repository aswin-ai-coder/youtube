from __future__ import annotations

import re

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.textinput import TextInput

from app.core.settings_service import SettingsService


class SettingsPage(TabbedPanelItem):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.settings = SettingsService()
        self.status = Label(text="", size_hint_y=None, height=36)
        self.content = self._build()

    def _build(self) -> BoxLayout:
        layout = BoxLayout(orientation="vertical", padding=12, spacing=8)
        self.theme = Spinner(text=self.settings.get("theme", "dark"), values=["dark", "light"], size_hint_y=None, height=44)
        self.accent_color = TextInput(text=self.settings.get("accent_color", "#2563eb"), multiline=False, hint_text="#RRGGBB", size_hint_y=None, height=44)
        self.language = TextInput(text=self.settings.get("language", "en"), multiline=False, hint_text="en", size_hint_y=None, height=44)
        self.folder = TextInput(text=self.settings.get("download_folder", ""), multiline=False, size_hint_y=None, height=44)
        self.ffmpeg_path = TextInput(text=self.settings.get("ffmpeg_path", ""), multiline=False, size_hint_y=None, height=44)
        self.concurrent_downloads = TextInput(text=str(self.settings.get("concurrent_downloads", 2)), multiline=False, input_filter="int", size_hint_y=None, height=44)
        self.concurrent_fragments = TextInput(text=str(self.settings.get("concurrent_fragments", 4)), multiline=False, input_filter="int", size_hint_y=None, height=44)
        self.retries = TextInput(text=str(self.settings.get("max_retries", 10)), multiline=False, input_filter="int", size_hint_y=None, height=44)
        self.notifications = CheckBox(active=bool(self.settings.get("notifications", True)))
        self.clipboard_monitoring = CheckBox(active=bool(self.settings.get("clipboard_monitoring", True)))
        save_btn = Button(text="Save Settings", size_hint_y=None, height=48)
        save_btn.bind(on_press=self.save)
        fields = [
            ("Theme", self.theme),
            ("Accent color", self.accent_color),
            ("Language", self.language),
            ("Download folder", self.folder),
            ("FFmpeg path", self.ffmpeg_path),
            ("Concurrent downloads", self.concurrent_downloads),
            ("Concurrent fragments", self.concurrent_fragments),
            ("Max retries", self.retries),
        ]
        for label, widget in fields:
            layout.add_widget(Label(text=label, size_hint_y=None, height=28))
            layout.add_widget(widget)
        for label, widget in (("Notifications", self.notifications), ("Clipboard monitoring", self.clipboard_monitoring)):
            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=34)
            row.add_widget(Label(text=label))
            row.add_widget(widget)
            layout.add_widget(row)
        layout.add_widget(save_btn)
        layout.add_widget(self.status)
        return layout

    @staticmethod
    def _bounded_int(value: str, default: int, minimum: int, maximum: int) -> int:
        try:
            parsed = int(value)
        except ValueError:
            return default
        return max(minimum, min(maximum, parsed))

    @staticmethod
    def _valid_hex(value: str) -> bool:
        return bool(re.fullmatch(r"#[0-9A-Fa-f]{6}", value))

    def save(self, *_args) -> None:
        accent = self.accent_color.text.strip()
        if not self._valid_hex(accent):
            self.status.text = "Accent color must look like #RRGGBB"
            return
        folder = self.folder.text.strip()
        if not folder:
            self.status.text = "Download folder is required"
            return
        self.settings.update(
            {
                "theme": self.theme.text if self.theme.text in {"dark", "light"} else "dark",
                "accent_color": accent,
                "language": self.language.text.strip() or "en",
                "download_folder": folder,
                "ffmpeg_path": self.ffmpeg_path.text.strip(),
                "concurrent_downloads": self._bounded_int(self.concurrent_downloads.text, 2, 1, 8),
                "concurrent_fragments": self._bounded_int(self.concurrent_fragments.text, 4, 1, 32),
                "max_retries": self._bounded_int(self.retries.text, 10, 0, 50),
                "notifications": bool(self.notifications.active),
                "clipboard_monitoring": bool(self.clipboard_monitoring.active),
            }
        )
        self.settings.save()
        self.status.text = "Saved"
