from kivymd.app import MDApp

from kivymd.uix.screenmanager import MDScreenManager

from kivymd.uix.navigationbar import (
    MDNavigationBar,
    MDNavigationItem,
    MDNavigationItemIcon,
    MDNavigationItemLabel,
)

from kivymd.uix.boxlayout import MDBoxLayout

from app.ui.android.screens.home_screen import HomeScreen
from app.ui.android.screens.queue_screen import QueueScreen
from app.ui.android.screens.history_screen import HistoryScreen
from app.ui.android.screens.settings_screen import SettingsScreen


class YouTubeDownloaderApp(MDApp):

    def build(self):

        self.title = "YouTube Downloader"

        self.theme_cls.theme_style = "Dark"

        self.theme_cls.primary_palette = "Blue"

        root = MDBoxLayout(
            orientation="vertical"
        )

        self.sm = MDScreenManager()

        self.sm.add_widget(HomeScreen(name="home"))
        self.sm.add_widget(QueueScreen(name="queue"))
        self.sm.add_widget(HistoryScreen(name="history"))
        self.sm.add_widget(SettingsScreen(name="settings"))

        nav = MDNavigationBar()

        home = MDNavigationItem()

        home.add_widget(
            MDNavigationItemIcon(
                icon="home",
            )
        )

        home.add_widget(
            MDNavigationItemLabel(
                text="Home",
            )
        )

        queue = MDNavigationItem()

        queue.add_widget(
            MDNavigationItemIcon(
                icon="download",
            )
        )

        queue.add_widget(
            MDNavigationItemLabel(
                text="Queue",
            )
        )

        history = MDNavigationItem()

        history.add_widget(
            MDNavigationItemIcon(
                icon="history",
            )
        )

        history.add_widget(
            MDNavigationItemLabel(
                text="History",
            )
        )

        settings = MDNavigationItem()

        settings.add_widget(
            MDNavigationItemIcon(
                icon="cog",
            )
        )

        settings.add_widget(
            MDNavigationItemLabel(
                text="Settings",
            )
        )

        home.bind(
            on_release=lambda x: self.change("home")
        )

        queue.bind(
            on_release=lambda x: self.change("queue")
        )

        history.bind(
            on_release=lambda x: self.change("history")
        )

        settings.bind(
            on_release=lambda x: self.change("settings")
        )

        nav.add_widget(home)
        nav.add_widget(queue)
        nav.add_widget(history)
        nav.add_widget(settings)

        root.add_widget(self.sm)
        root.add_widget(nav)

        return root

    def change(self, screen):

        self.sm.current = screen


if __name__ == "__main__":
    YouTubeDownloaderApp().run()
