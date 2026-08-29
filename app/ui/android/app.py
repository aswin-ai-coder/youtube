from kivymd.app import MDApp
from app.core.theme_service import ThemeService
from kivymd.uix.screenmanager import MDScreenManager
from kivy.uix.screenmanager import SlideTransition
from app.ui.android.widgets.bottom_nav import BottomNav

from kivymd.uix.boxlayout import MDBoxLayout

from app.ui.android.screens.home_screen import HomeScreen
from app.ui.android.screens.queue_screen import QueueScreen
from app.ui.android.screens.history_screen import HistoryScreen
from app.ui.android.screens.settings_screen import SettingsScreen
from app.ui.android.screens.favorites_screen import FavoritesScreen

class YouTubeDownloaderApp(MDApp):

    def build(self):
        self.title = "YouTube Downloader"
        self.theme = ThemeService()
        self.theme.apply(self)
        self.theme_cls.primary_palette = "Blue"

        root = MDBoxLayout(
            orientation="vertical"
        )

        self.sm = MDScreenManager()

        self.sm.add_widget(HomeScreen(name="home"))
        self.sm.add_widget(QueueScreen(name="queue"))
        self.sm.add_widget(HistoryScreen(name="history"))

        # Only if FavoritesScreen exists
        self.sm.add_widget(FavoritesScreen(name="favorites"))

        self.sm.add_widget(SettingsScreen(name="settings"))

        self.nav = BottomNav(self.change)

        root.add_widget(self.sm)
        root.add_widget(self.nav)

        self.change("home")
        return root

    def change(self, screen):
        self.sm.transition = SlideTransition(
            direction="left",
            duration=0.2,
        )

        self.sm.current = screen


if __name__ == "__main__":
    YouTubeDownloaderApp().run()
