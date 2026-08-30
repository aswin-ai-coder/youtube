from __future__ import annotations

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.widget import Widget

from app.core.theme_service import ThemeService
from app.ui.android.screens.favorites_screen import FavoritesScreen
from app.ui.android.screens.history_screen import HistoryScreen
from app.ui.android.screens.home_screen import HomeScreen
from app.ui.android.screens.queue_screen import QueueScreen
from app.ui.android.screens.settings_screen import SettingsScreen
from app.ui.android.widgets.bottom_nav import BottomNav


class YouTubeDownloaderApp(MDApp):
    """Android application entry point.

    Keep startup work minimal so the first frame is the real application UI,
    not a static loading/splash screen. Heavy services are initialized by the
    individual screens only when they are needed.
    """

    def build(self):
        self.title = "YouTube Downloader"
        self.theme = ThemeService()
        self.theme.apply(self)

        # Avoid leaving a blank/native-looking launch surface visible while
        # Kivy builds the widget tree. The Android launcher handles its own
        # launch transition; Kivy should render our UI as soon as possible.
        try:
            Window.clearcolor = self.theme_cls.backgroundColor
        except Exception:
            pass

        root = MDBoxLayout(orientation="vertical")
        self.sm = MDScreenManager()

        # Construct only the visible screen first. Remaining screens are added
        # on the next frame so startup remains responsive.
        self.home = HomeScreen(name="home")
        self.sm.add_widget(self.home)

        root.add_widget(self.sm)
        self.nav = None

        Clock.schedule_once(self._finish_ui_setup, 0)
        return root

    def _finish_ui_setup(self, _dt):
        # Add secondary screens after the first frame is on screen.
        for screen in (
            QueueScreen(name="queue"),
            HistoryScreen(name="history"),
            FavoritesScreen(name="favorites"),
            SettingsScreen(name="settings"),
        ):
            self.sm.add_widget(screen)

        self.nav = BottomNav(self.change)
        self.root.add_widget(self.nav)
        self.change("home")

    def change(self, screen: str):
        if screen in self.sm.screen_names:
            self.sm.current = screen

    def on_stop(self):
        # Keep shutdown deterministic and avoid leaving worker threads alive.
        home = getattr(self, "home", None)
        coordinator = getattr(home, "coordinator", None)
        if coordinator is not None:
            try:
                coordinator.shutdown()
            except Exception:
                pass
        return super().on_stop()


if __name__ == "__main__":
    YouTubeDownloaderApp().run()
