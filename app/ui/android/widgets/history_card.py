from pathlib import Path

from kivy.metrics import dp

from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import (
    MDButton,
    MDButtonText,
)

from kivy.utils import platform

import subprocess
import os


class HistoryCard(MDCard):

    def __init__(self, record, **kwargs):
        super().__init__(**kwargs)

        self.record = record

        self.orientation = "vertical"

        self.padding = dp(16)

        self.spacing = dp(12)

        self.adaptive_height = True

        self.radius = [20]

        self.add_widget(

            MDLabel(
                text=record.title,
                bold=True,
                adaptive_height=True,
            )
        )

        self.add_widget(

            MDLabel(
                text=record.status,
                adaptive_height=True,
            )
        )

        row = MDBoxLayout(
            adaptive_height=True,
            spacing=dp(10),
        )

        open_btn = MDButton(style="outlined")
        open_btn.add_widget(
            MDButtonText(text="OPEN")
        )

        folder_btn = MDButton(style="outlined")
        folder_btn.add_widget(
            MDButtonText(text="FOLDER")
        )

        row.add_widget(open_btn)
        row.add_widget(folder_btn)

        self.add_widget(row)

        open_btn.bind(
            on_release=self.open_file
        )

        folder_btn.bind(
            on_release=self.open_folder
        )

    def open_file(self, *_):

        path = getattr(self.record, "output_path", "")

        if not path:
            return

        if platform == "linux":

            subprocess.Popen(
                ["xdg-open", path]
            )

    def open_folder(self, *_):

        path = getattr(self.record, "output_path", "")

        if not path:
            return

        folder = str(Path(path).parent)

        if platform == "linux":

            subprocess.Popen(
                ["xdg-open", folder]
            )
