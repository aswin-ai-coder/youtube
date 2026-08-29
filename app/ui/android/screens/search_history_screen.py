from kivymd.uix.screen import MDScreen
from kivymd.uix.list import (
    MDListItem,
    MDListItemHeadlineText,
    MDListItemSupportingText,
)
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout

from app.core.search_history_service import SearchHistoryService


class SearchHistoryScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.history = SearchHistoryService()

        scroll = MDScrollView()

        self.container = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
        )

        scroll.add_widget(self.container)

        self.add_widget(scroll)

    def on_pre_enter(self):

        self.container.clear_widgets()

        for url, title, date in self.history.latest():

            item = MDListItem()

            item.add_widget(
                MDListItemHeadlineText(
                    text=title,
                )
            )

            item.add_widget(
                MDListItemSupportingText(
                    text=date,
                )
            )

            self.container.add_widget(item)
