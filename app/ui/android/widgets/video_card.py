from kivy.metrics import dp

from kivy.uix.image import AsyncImage

from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel


class VideoCard(MDCard):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.adaptive_height = True
        self.padding = dp(18)
        self.spacing = dp(16)
        self.radius = [24]

        self.thumbnail = AsyncImage(
            size_hint_y=None,
            height=dp(200),
            fit_mode="cover",
        )

        self.add_widget(self.thumbnail)

        self.info = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing=dp(8),
        )

        self.title = MDLabel(
            text="No video selected",
            bold=True,
            adaptive_height=True,
        )

        self.channel = MDLabel(
            text="",
            adaptive_height=True,
        )

        self.details = MDLabel(
            text="",
            adaptive_height=True,
        )

        self.info.add_widget(self.title)
        self.info.add_widget(self.channel)
        self.info.add_widget(self.details)

        self.add_widget(self.info)

    def update(self, metadata):

        self.title.text = metadata.title or ""

        self.channel.text = metadata.channel or ""

        self.details.text = (
            f"{metadata.best_resolution or ''}   •   "
            f"{metadata.best_video_codec or ''}   •   "
            f"{metadata.best_audio_codec or ''}"
        )

        if metadata.thumbnail:
            self.thumbnail.source = metadata.thumbnail

    def set_title(self, value):
        self.title.text = value

    def set_channel(self, value):
        self.channel.text = value

    def set_details(self, value):
        self.details.text = value

    def set_thumbnail(self, url):
        self.thumbnail.source = url
