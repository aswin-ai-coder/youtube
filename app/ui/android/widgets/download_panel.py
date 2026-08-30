from kivy.metrics import dp
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import (
    MDButton,
    MDButtonText,
)
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.progressindicator import MDLinearProgressIndicator
from kivymd.uix.segmentedbutton import (
    MDSegmentedButton,
    MDSegmentedButtonItem,
    MDSegmentButtonLabel,
)


class DownloadPanel(MDCard):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.adaptive_height = True
        self.padding = dp(20)
        self.spacing = dp(16)
        self.radius = [24]

        self.metadata = None

        # ---------------- Download Type ----------------

        self.add_widget(
            MDLabel(
                text="Download Type",
                bold=True,
                adaptive_height=True,
            )
        )

        self.type_selector = MDSegmentedButton()

        self.type = "Video+Audio"

        for name in (
            "Video",
            "Audio",
            "Video+Audio",
        ):

            item = MDSegmentedButtonItem()

            item.add_widget(
                MDSegmentButtonLabel(
                    text=name,
                )
            )

            item.bind(
                on_release=lambda x, n=name: self.select_type(n)
            )

            self.type_selector.add_widget(item)

        self.add_widget(self.type_selector)

        # ---------------- Quality ----------------

        self.add_widget(
            MDLabel(
                text="Quality",
                adaptive_height=True,
            )
        )

        self.quality = "Best"

        self.quality_button = MDButton(
            style="outlined",
            size_hint_y=None,
            height=dp(46),
        )

        self.quality_text = MDButtonText(
            text="Best"
        )

        self.quality_button.add_widget(
            self.quality_text
        )

        self.add_widget(self.quality_button)

        self.menu = MDDropdownMenu(
            caller=self.quality_button,
            items=[],
        )

        self.quality_button.bind(
            on_release=lambda x: self.menu.open()
        )
        self.add_widget(
            MDLabel(
                text="Subtitles",
                adaptive_height=True,
            )

        )

        self.subtitle = MDCheckbox(
            active=False,
        )

        self.add_widget(self.subtitle)
        # ---------------- Status ----------------

        self.status = MDLabel(
            text="Ready",
            adaptive_height=True,
        )

        self.add_widget(self.status)

        self.progress = MDLinearProgressIndicator(
            value=0,
        )

        self.add_widget(self.progress)

        self.percent = MDLabel(
            text="0%",
            adaptive_height=True,
        )

        self.add_widget(self.percent)

        self.speed = MDLabel(
            text="Speed: --",
            adaptive_height=True,
        )

        self.add_widget(self.speed)

        self.size = MDLabel(
            text="Size: -- / --",
            adaptive_height=True,
        )

        self.add_widget(self.size)

        self.eta = MDLabel(
            text="ETA: --",
            adaptive_height=True,
        )

        self.add_widget(self.eta)

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

        self.add_widget(self.download_button)

    # --------------------------------------------------

    def load_metadata(self, metadata):

        self.metadata = metadata

        qualities = ["Best"]

        if getattr(metadata, "qualities", None):
            qualities.extend(metadata.qualities)

        self.menu.items = []

        for quality in qualities:

            self.menu.items.append(
                {
                    "text": quality,
                    "on_release": lambda q=quality: self.select_quality(q),
                }
            )

    def select_quality(self, quality):

        self.quality = quality

        self.quality_text.text = quality

        self.menu.dismiss()

    def select_type(self, value):

        self.type = value

    # --------------------------------------------------

    def set_progress(self, value):

        self.progress.value = value

        self.percent.text = f"{int(value)}%"

    def set_status(self, text):

        self.status.text = text

    def set_speed(self, text):

        self.speed.text = f"Speed: {text}"


    def set_size(self, downloaded, total):

        self.size.text = f"Size: {downloaded} / {total}"


    def set_eta(self, text):

        self.eta.text = f"ETA: {text}"

    def finish(self):

        self.progress.value = 100

        self.percent.text = "100%"

        self.status.text = "Completed"

    def error(self):

        self.status.text = "Download Failed"

    # --------------------------------------------------

    def selected_quality(self):

        return self.quality

    def selected_type(self):

        return self.type

    def subtitles_enabled(self):

        return self.subtitle.active

