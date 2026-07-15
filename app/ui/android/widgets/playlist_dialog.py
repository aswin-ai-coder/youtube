from kivy.metrics import dp

from kivymd.uix.dialog import MDDialog
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText

from app.ui.android.widgets.playlist_item import PlaylistItem


class PlaylistDialog(MDDialog):

    def __init__(self, videos, callback, **kwargs):
        super().__init__(**kwargs)

        self.callback = callback
        self.items = []

        root = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing=dp(12),
        )

        scroll = MDScrollView()

        box = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
        )

        for video in videos:

            item = PlaylistItem(video)

            self.items.append(item)

            box.add_widget(item)

        scroll.add_widget(box)

        root.add_widget(scroll)

        btn = MDButton(style="filled")
        btn.add_widget(MDButtonText(text="DOWNLOAD"))

        btn.bind(on_release=self.finish)

        root.add_widget(btn)

        self.add_widget(root)

    def finish(self, *_):

        selected = [
            item.video
            for item in self.items
            if item.selected()
        ]

        self.dismiss()

        self.callback(selected)
