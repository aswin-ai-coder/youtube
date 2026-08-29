from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import (
    MDListItem,
    MDListItemHeadlineText,
)

from app.core.favorites_service import FavoritesService


class FavoritesScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.service = FavoritesService()

        scroll = MDScrollView()

        self.container = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
        )

        scroll.add_widget(self.container)

        self.add_widget(scroll)

    def on_pre_enter(self):

        self.container.clear_widgets()

        for url, title, thumbnail in self.service.all():

            item = MDListItem()

            item.add_widget(
                MDListItemHeadlineText(
                    text=title,
                )
            )

            self.container.add_widget(item)
