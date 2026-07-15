from kivy.metrics import dp

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import (
    MDButton,
    MDButtonIcon,
    MDButtonText,
)


class BottomNav(MDBoxLayout):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.orientation = "horizontal"

        self.adaptive_height = True

        self.spacing = dp(8)

        self.padding = dp(12)

        self.add_widget(self.make_button("home", "Home"))
        self.add_widget(self.make_button("download", "Queue"))
        self.add_widget(self.make_button("history", "History"))
        self.add_widget(self.make_button("cog", "Settings"))

    def make_button(self, icon, text):

        button = MDButton(style="text")

        button.add_widget(
            MDButtonIcon(icon=icon)
        )

        button.add_widget(
            MDButtonText(text=text)
        )

        return button
