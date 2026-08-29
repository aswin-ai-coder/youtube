from kivy.metrics import dp

from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.progressindicator import MDLinearProgressIndicator


class PlaylistProgress(MDCard):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.adaptive_height = True
        self.padding = dp(16)
        self.spacing = dp(12)
        self.radius = [18]

        self.title = MDLabel(
            text="Playlist",
            bold=True,
            adaptive_height=True,
        )

        self.index = MDLabel(
            text="0 / 0",
            adaptive_height=True,
        )

        self.progress = MDLinearProgressIndicator(
            value=0,
        )

        self.add_widget(self.title)
        self.add_widget(self.index)
        self.add_widget(self.progress)

    def update(self, current, total):

        self.index.text = f"{current} / {total}"

        if total:

            self.progress.value = current * 100 / total
