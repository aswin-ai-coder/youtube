from __future__ import annotations

from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel

from app.ui.mobile.download import DownloadPage
from app.ui.mobile.history import HistoryPage
from app.ui.mobile.queue import QueuePage
from app.ui.mobile.settings import SettingsPage


class YouTubeDownloaderMobileApp(App):
    title = "YouTube Downloader"

    def build(self):
        tabs = TabbedPanel(do_default_tab=False)
        tabs.add_widget(DownloadPage(text="Downloads"))
        tabs.add_widget(QueuePage(text="Queue"))
        tabs.add_widget(HistoryPage(text="History"))
        tabs.add_widget(SettingsPage(text="Settings"))
        return tabs


def main() -> None:
    YouTubeDownloaderMobileApp().run()


if __name__ == "__main__":
    main()
