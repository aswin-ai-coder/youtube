from kivy.metrics import dp

from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.progressindicator import MDLinearProgressIndicator
from kivymd.uix.button import MDButton, MDButtonText


class QueueItem(MDCard):

    def __init__(self, item_id, title, callbacks, **kwargs):
        super().__init__(**kwargs)

        self.item_id = item_id

        self.orientation = "vertical"
        self.adaptive_height = True
        self.padding = dp(16)
        self.spacing = dp(12)
        self.radius = [20]

        self.add_widget(
            MDLabel(
                text=title,
                bold=True,
                adaptive_height=True,
            )
        )

        self.status = MDLabel(
            text="Waiting...",
            adaptive_height=True,
        )

        self.add_widget(self.status)

        self.progress = MDLinearProgressIndicator(value=0)
        self.add_widget(self.progress)

        self.percent = MDLabel(
            text="0%",
            adaptive_height=True,
        )

        self.add_widget(self.percent)

        buttons = MDBoxLayout(
            adaptive_height=True,
            spacing=dp(8),
        )

        pause = MDButton(style="outlined")
        pause.add_widget(MDButtonText(text="Pause"))

        resume = MDButton(style="outlined")
        resume.add_widget(MDButtonText(text="Resume"))

        cancel = MDButton(style="outlined")
        cancel.add_widget(MDButtonText(text="Cancel"))

        pause.bind(
            on_release=lambda *_: callbacks["pause"](self.item_id)
        )

        resume.bind(
            on_release=lambda *_: callbacks["resume"](self.item_id)
        )

        cancel.bind(
            on_release=lambda *_: callbacks["cancel"](self.item_id)
        )

        buttons.add_widget(pause)
        buttons.add_widget(resume)
        buttons.add_widget(cancel)

        self.add_widget(buttons)

    def update_progress(self, value):

        self.progress.value = value
        self.percent.text = f"{int(value)}%"

    def update_status(self, text):

        self.status.text = text
