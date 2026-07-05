from __future__ import annotations

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.widget import Widget

from core.history_service import HistoryService


class HistoryPage(TabbedPanelItem):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.history = HistoryService()
        self.list_layout = BoxLayout(
            orientation="vertical", spacing=6, size_hint_y=None
        )
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))
        self.content = self._build()
        self.refresh()

    def _build(self) -> BoxLayout:
        layout = BoxLayout(orientation="vertical", padding=12, spacing=8)
        refresh_btn = Button(text="Refresh", size_hint_y=None, height=48)
        refresh_btn.bind(on_press=lambda *_args: self.refresh())
        scroll = ScrollView()
        scroll.add_widget(self.list_layout)
        layout.add_widget(refresh_btn)
        layout.add_widget(scroll)
        return layout

    def refresh(self) -> None:
        self.list_layout.clear_widgets()
        for record in self.history.search(limit=100):
            row = BoxLayout(
                orientation="horizontal", size_hint_y=None, height=48, spacing=6
            )
            row.add_widget(Label(text=f"{record['title']}", size_hint_x=0.4))
            row.add_widget(Label(text=f"{record['status']}", size_hint_x=0.15))
            row.add_widget(Label(text=f"{record['date']}", size_hint_x=0.25))
            actions = BoxLayout(orientation="horizontal", size_hint_x=0.2, spacing=4)
            open_btn = Button(text="Open", size_hint_x=None, width=70)
            open_btn.bind(
                on_press=lambda _btn, record_id=record["id"]: self._open_file(record_id)
            )
            folder_btn = Button(text="Folder", size_hint_x=None, width=70)
            folder_btn.bind(
                on_press=lambda _btn, record_id=record["id"]: self._open_folder(
                    record_id
                )
            )
            delete_btn = Button(text="Delete", size_hint_x=None, width=70)
            delete_btn.bind(
                on_press=lambda _btn, record_id=record["id"]: self._delete(record_id)
            )
            actions.add_widget(open_btn)
            actions.add_widget(folder_btn)
            actions.add_widget(delete_btn)
            row.add_widget(actions)
            self.list_layout.add_widget(row)
        self.list_layout.add_widget(Widget(size_hint_y=None, height=8))

    def _open_file(self, record_id: int) -> None:
        record = self.history.get(record_id)
        if not record:
            return
        # On Android, we cannot reliably open a file without platform integration.
        self.content.add_widget(
            Label(
                text=f"Open file: {record['output_path']}", size_hint_y=None, height=30
            )
        )

    def _open_folder(self, record_id: int) -> None:
        record = self.history.get(record_id)
        if not record:
            return
        self.content.add_widget(
            Label(
                text=f"Open folder: {record['output_path']}",
                size_hint_y=None,
                height=30,
            )
        )

    def _delete(self, record_id: int) -> None:
        self.history.delete(record_id)
        self.refresh()
