from kivy.metrics import dp

from kivymd.uix.bottomsheet import MDBottomSheet
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu


class DownloadSheet(MDBottomSheet):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.metadata = None

        content = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing=dp(18),
            padding=dp(20),
        )

        content.add_widget(
            MDLabel(
                text="Download Options",
                bold=True,
                adaptive_height=True,
            )
        )

        self.quality_button = MDButton(
            style="outlined",
            size_hint_y=None,
            height=dp(48),
        )

        self.quality_text = MDButtonText(
            text="Best"
        )

        self.quality_button.add_widget(self.quality_text)

        content.add_widget(self.quality_button)

        self.menu = MDDropdownMenu(
            caller=self.quality_button,
            items=[],
        )

        self.quality_button.bind(
            on_release=lambda x: self.menu.open()
        )

        self.download_button = MDButton(
            style="filled",
            size_hint_y=None,
            height=dp(54),
        )

        self.download_button.add_widget(
            MDButtonText(
                text="DOWNLOAD"
            )
        )

        content.add_widget(self.download_button)

        self.add_widget(content)

    def load_metadata(self, metadata):

        self.metadata = metadata

        self.menu.items = []

        qualities = ["Best"]

        if getattr(metadata, "qualities", None):
            qualities.extend(metadata.qualities)

        for q in qualities:

            self.menu.items.append(
                {
                    "text": q,
                    "on_release": lambda x=q: self.select_quality(x),
                }
            )

    def select_quality(self, q):

        self.quality_text.text = q

        self.menu.dismiss()

    def selected_quality(self):

        return self.quality_text.text
