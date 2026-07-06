from __future__ import annotations

from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.widget import Widget

from app.ui.mobile.state import mobile_manager


class QueuePage(TabbedPanelItem):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.list_layout = BoxLayout(
            orientation="vertical", spacing=6, size_hint_y=None
        )
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))
        self.content = self._build()
        Clock.schedule_interval(lambda _dt: self.refresh(), 2)

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
        for item in mobile_manager.queue.list_items():
            title = item.title or item.url
            status = item.status.value
            progress = item.progress
            row = BoxLayout(
                orientation="horizontal", size_hint_y=None, height=48, spacing=6
            )
            row.add_widget(Label(text=f"{title}", size_hint_x=0.45))
            row.add_widget(Label(text=f"{status}", size_hint_x=0.2))
            row.add_widget(Label(text=f"{progress}%", size_hint_x=0.15))
            actions = BoxLayout(orientation="horizontal", size_hint_x=0.2, spacing=4)
            pause_btn = Button(text="Pause", size_hint_x=None, width=70)
            pause_btn.bind(
                on_press=lambda _btn, item_id=item.id: mobile_manager.pause(item_id)
            )
            resume_btn = Button(text="Resume", size_hint_x=None, width=70)
            resume_btn.bind(
                on_press=lambda _btn, item_id=item.id: mobile_manager.resume(item_id)
            )
            cancel_btn = Button(text="Cancel", size_hint_x=None, width=70)
            cancel_btn.bind(
                on_press=lambda _btn, item_id=item.id: mobile_manager.cancel(item_id)
            )
            retry_btn = Button(text="Retry", size_hint_x=None, width=70)
            retry_btn.bind(
                on_press=lambda _btn, item_id=item.id: mobile_manager.retry(item_id)
            )
            actions.add_widget(pause_btn)
            actions.add_widget(resume_btn)
            actions.add_widget(cancel_btn)
            actions.add_widget(retry_btn)
            row.add_widget(actions)
            self.list_layout.add_widget(row)
        self.list_layout.add_widget(Widget(size_hint_y=None, height=8))
