from kivy.metrics import dp

from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.progressindicator import MDLinearProgressIndicator


class QueueCard(MDCard):

    def __init__(self, item, manager, **kwargs):
        super().__init__(**kwargs)

        self.item = item
        self.manager = manager

        self.orientation = "vertical"
        self.padding = dp(16)
        self.spacing = dp(12)
        self.radius = [18]
        self.adaptive_height = True

        self.title = MDLabel(
            text=item.title,
            bold=True,
            adaptive_height=True,
        )

        self.status = MDLabel(
            text=item.status,
            adaptive_height=True,
        )

        self.progress = MDLinearProgressIndicator(
            value=item.progress,
        )

        buttons = MDBoxLayout(
            adaptive_height=True,
            spacing=dp(8),
        )

        self.pause = MDButton(style="outlined")
        self.pause.add_widget(MDButtonText(text="Pause"))

        self.resume = MDButton(style="outlined")
        self.resume.add_widget(MDButtonText(text="Resume"))

        self.cancel = MDButton(style="text")
        self.cancel.add_widget(MDButtonText(text="Cancel"))

        self.pause.bind(on_release=self.pause_download)
        self.resume.bind(on_release=self.resume_download)
        self.cancel.bind(on_release=self.cancel_download)

        buttons.add_widget(self.pause)
        buttons.add_widget(self.resume)
        buttons.add_widget(self.cancel)

        self.add_widget(self.title)
        self.add_widget(self.status)
        self.add_widget(self.progress)
        self.add_widget(buttons)

    def pause_download(self, *args):
        self.manager.coordinator.pause(self.item.id)

    def resume_download(self, *args):
        self.manager.coordinator.resume(self.item.id)

    def cancel_download(self, *args):
        self.manager.coordinator.cancel(self.item.id)
