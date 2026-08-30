from __future__ import annotations

import traceback

from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.screenmanager import MDScreenManager
from kivy.uix.screenmanager import SlideTransition


class YouTubeDownloaderApp(MDApp):
    """Android application entry point with safe first-frame startup."""

    def build(self):
        self.title = "YouTube Downloader"
        self.sm = MDScreenManager()
        self._root = MDBoxLayout(orientation="vertical")
        self._root.add_widget(self.sm)
        self._ui_ready = False
        self.clipboard_service = None
        return self._root

    def on_start(self):
        self._hide_android_loading_screen()
        Clock.schedule_once(self._initialize_ui, 0)

    def _hide_android_loading_screen(self, *_args):
        try:
            from android import loadingscreen
            loadingscreen.hide_loading_screen()
        except (ImportError, AttributeError, RuntimeError):
            pass

    def _initialize_ui(self, *_args):
        if self._ui_ready:
            return
        try:
            from app.core.theme_service import ThemeService
            from app.ui.android.screens.favorites_screen import FavoritesScreen
            from app.ui.android.screens.history_screen import HistoryScreen
            from app.ui.android.screens.home_screen import HomeScreen
            from app.ui.android.screens.queue_screen import QueueScreen
            from app.ui.android.screens.settings_screen import SettingsScreen
            from app.ui.android.widgets.bottom_nav import BottomNav

            self.theme = ThemeService()
            self.theme.apply(self)

            self.sm.add_widget(HomeScreen(name="home"))
            self.sm.add_widget(QueueScreen(name="queue"))
            self.sm.add_widget(HistoryScreen(name="history"))
            self.sm.add_widget(FavoritesScreen(name="favorites"))
            self.sm.add_widget(SettingsScreen(name="settings"))
            self.sm.current = "home"

            self.nav = BottomNav(self.change)
            self._root.add_widget(self.nav)
            self._ui_ready = True
        except Exception as exc:
            traceback.print_exc()
            self._show_startup_error(exc)

    def _show_startup_error(self, exc):
        self.sm.clear_widgets()
        self.sm.add_widget(
            MDLabel(
                text=(
                    "YouTube Downloader\n\n"
                    "The Android UI could not start.\n\n"
                    f"{type(exc).__name__}: {exc}"
                ),
                halign="center",
                valign="middle",
                padding=(dp(24), dp(24)),
            )
        )

    def change(self, screen: str):
        if self._ui_ready and screen in self.sm.screen_names:
            self.sm.transition = SlideTransition(direction="left", duration=0.2)
            self.sm.current = screen

    def on_stop(self):
        clipboard = getattr(self, "clipboard_service", None)
        if clipboard is not None:
            try:
                clipboard.shutdown()
            except Exception:
                pass
        return super().on_stop()


if __name__ == "__main__":
    YouTubeDownloaderApp().run()
