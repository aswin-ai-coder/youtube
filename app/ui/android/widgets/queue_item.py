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

        self.status = MDLabel(text="Queued", adaptive_height=True)
        self.add_widget(self.status)

        self.progress = MDLinearProgressIndicator(value=0)
        self.add_widget(self.progress)

        self.percent = MDLabel(text="0%", adaptive_height=True)
        self.add_widget(self.percent)

        self.stats = MDLabel(
            text="Speed: --   •   Size: 0 B / --   •   ETA: --",
            adaptive_height=True,
        )
        self.add_widget(self.stats)

        buttons = MDBoxLayout(adaptive_height=True, spacing=dp(8))

        pause = MDButton(style="outlined")
        pause.add_widget(MDButtonText(text="Pause"))
        resume = MDButton(style="outlined")
        resume.add_widget(MDButtonText(text="Resume"))
        cancel = MDButton(style="outlined")
        cancel.add_widget(MDButtonText(text="Cancel"))

        pause.bind(on_release=lambda *_: callbacks["pause"](self.item_id))
        resume.bind(on_release=lambda *_: callbacks["resume"](self.item_id))
        cancel.bind(on_release=lambda *_: callbacks["cancel"](self.item_id))

        buttons.add_widget(pause)
        buttons.add_widget(resume)
        buttons.add_widget(cancel)
        self.add_widget(buttons)

    def update_progress(self, value):
        self.progress.value = max(0, min(float(value), 100))
        self.percent.text = f"{int(value)}%"

    def update_status(self, text):
        self.status.text = text

    def update_speed(self, text):
        parts = self.stats.text.split("   •   ")
        size = parts[1] if len(parts) > 1 else "Size: 0 B / --"
        eta = parts[2] if len(parts) > 2 else "ETA: --"
        self.stats.text = f"Speed: {text}   •   {size}   •   {eta}"

    def update_size(self, downloaded, total):
        parts = self.stats.text.split("   •   ")
        speed = parts[0] if parts else "Speed: --"
        eta = parts[2] if len(parts) > 2 else "ETA: --"
        self.stats.text = f"{speed}   •   Size: {downloaded} / {total}   •   {eta}"

    def update_eta(self, text):
        parts = self.stats.text.split("   •   ")
        speed = parts[0] if parts else "Speed: --"
        size = parts[1] if len(parts) > 1 else "Size: 0 B / --"
        self.stats.text = f"{speed}   •   {size}   •   ETA: {text}"
