from kivymd.uix.list import MDListItem
from kivymd.uix.list import MDListItemHeadlineText
from kivymd.uix.selectioncontrol import MDCheckbox


class PlaylistItem(MDListItem):

    def __init__(self, video, **kwargs):
        super().__init__(**kwargs)

        self.video = video

        self.checkbox = MDCheckbox(
            active=True,
        )

        self.add_widget(self.checkbox)

        self.add_widget(
            MDListItemHeadlineText(
                text=video["title"],
            )
        )

    def selected(self):
        return self.checkbox.active
