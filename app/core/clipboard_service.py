from kivy.clock import Clock
from kivy.core.clipboard import Clipboard


class ClipboardService:

    def __init__(self, callback):

        self.callback = callback
        self.last_text = ""

        Clock.schedule_interval(
            self.check,
            1,
        )

    def check(self, dt):

        try:

            text = Clipboard.paste().strip()

        except Exception:
            return

        if not text:
            return

        if text == self.last_text:
            return

        self.last_text = text

        if (
            "youtube.com" in text
            or "youtu.be" in text
        ):

            self.callback(text)
