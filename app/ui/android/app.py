from __future__ import annotations

from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screenmanager import MDScreenManager

from app.core.theme_service import ThemeService
from app.ui.android.screens.favorites_screen import FavoritesScreen
from app.ui.android.screens.history_screen import HistoryScreen
from app.ui.android.screens.home_screen import HomeScreen
from app.ui.android.screens.queue_screen import QueueScreen
from app.ui.android.screens.settings_screen import SettingsScreen
from app.ui.android.widgets.bottom_nav import BottomNav


class YouTubeDownloaderApp(MDApp):
    """Android application entry point with direct first-frame UI startup."""

    def build(self):
        self.title = "YouTube Downloader"
        self.theme = ThemeService()
        self.theme.apply(self)

        try:
            Window.clearcolor = self.theme_cls.backgroundColor
        except Exception:
            pass

        self.sm = MDScreenManager()
        self.sm.add_widget(HomeScreen(name="home"))
        self.sm.add_widget(QueueScreen(name="queue"))
        self.sm.add_widget(HistoryScreen(name="history"))
        self.sm.add_widget(FavoritesScreen(name="favorites"))
        self.sm.add_widget(SettingsScreen(name="settings"))
        self.sm.current = "home"

        self.nav = BottomNav(self.change)

        root = MDBoxLayout(orientation="vertical")
        root.add_widget(self.sm)
        root.add_widget(self.nav)
        return root

    def change(self, screen: str):
        if screen in self.sm.screen_names:
            self.sm.current = screen

    def on_stop(self):
        home = self.sm.get_screen("home") if hasattr(self, "sm") else None
        coordinator = getattr(home, "coordinator", None)
        if coordinator is not None:
            try:
                coordinator.shutdown()
            except Exception:
                pass
        return super().on_stop()


if __name__ == "__main__":
    YouTubeDownloaderApp().run()
