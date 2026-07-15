from kivy.metrics import dp

from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import (
    MDButton,
    MDButtonText,
)
from kivymd.uix.progressindicator import MDCircularProgressIndicator


class UrlBar(MDCard):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.adaptive_height = True
        self.padding = dp(18)
        self.spacing = dp(14)
        self.radius = [24]

        row = MDBoxLayout(
            adaptive_height=True,
            spacing=dp(12),
        )

        self.url_input = MDTextField(
            hint_text="Paste YouTube URL...",
            mode="outlined",
        )

        row.add_widget(self.url_input)

        self.analyze_button = MDButton(
            style="filled",
            size_hint_x=None,
            width=dp(120),
        )

        self.analyze_button.add_widget(
            MDButtonText(
                text="Analyze",
            )
        )

        row.add_widget(self.analyze_button)

        self.add_widget(row)

        self.loader = MDCircularProgressIndicator(
            size_hint=(None, None),
            size=(dp(36), dp(36)),
            active=False,
        )

        self.add_widget(self.loader)

    def set_loading(self, value):

        self.loader.active = value

        self.loader.opacity = 1 if value else 0

        self.analyze_button.disabled = value

    def show_error(self, text):

        self.url_input.error = True

        self.url_input.helper_text = text
