from threading import Thread
from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from app.core.playlist_service import PlaylistService
from app.ui.android.widgets.playlist_dialog import PlaylistDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from datetime import datetime
from app.core.youtube_service import YouTubeService
from app.core.queue_service import QueueService
from app.core.settings_service import SettingsService
from app.core.playlist_service import PlaylistMetadata
from app.core.notification_service import NotificationService
from app.ui.desktop.download_coordinator import DownloadCoordinator
from app.ui.desktop.queue_item_factory import QueueItemFactory

from app.utils.helpers import format_duration, format_number

from app.ui.android.widgets.url_bar import UrlBar
from app.ui.android.widgets.video_card import VideoCard
from app.ui.android.widgets.download_panel import DownloadPanel


class HomeScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.youtube = YouTubeService()
        self.playlists = PlaylistService()
        self.settings = SettingsService()
        self.notifications = NotificationService()
        self.queue = QueueService()

        self.coordinator = DownloadCoordinator(
            self.queue,
            self.settings,
            None,
        )

        self.factory = QueueItemFactory(self)

        self.metadata = None

        root = MDBoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(20),
        )

        scroll = MDScrollView()

        content = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing=dp(20),
            padding=[0, dp(8), 0, dp(30)],
        )

        self.url_bar = UrlBar()
        self.video_card = VideoCard()
        self.download_panel = DownloadPanel()

        self.url_bar.analyze_button.bind(
            on_release=self.analyze
        )

        self.download_panel.download_button.bind(
            on_release=self.download
        )

        content.add_widget(self.url_bar)
        content.add_widget(self.video_card)
        content.add_widget(self.download_panel)

        scroll.add_widget(content)

        root.add_widget(scroll)

        self.add_widget(root)

        # ---------- DownloadCoordinator Signals ----------

        self.coordinator.progress_changed.connect(
            self.update_progress
        )

        self.coordinator.status_changed.connect(
            self.update_status
        )

        self.coordinator.completed.connect(
            self.download_completed
        )

        self.coordinator.failed.connect(
            self.download_failed
        )

    def analyze(self, *args):

        url = self.url_bar.url_input.text.strip()

        if not url:
            return

        self.url_bar.set_loading(True)

        Thread(
            target=self._worker,
            args=(url,),
            daemon=True,
        ).start()

    def _worker(self, url):

        try:

            playlist = self.playlists.get_playlist_info(url)

            if playlist.is_playlist:

                Clock.schedule_once(
                    lambda dt: self.show_playlist(playlist)
                )

            metadata = self.youtube.get_video_info(url)

            self.metadata = metadata

            Clock.schedule_once(
                lambda dt: self.update_ui(metadata)
            )

        except Exception as e:

            Clock.schedule_once(
                lambda dt: self.url_bar.show_error(str(e))
            )

        finally:

            Clock.schedule_once(
                lambda dt: self.url_bar.set_loading(False)
            )

    def show_playlist(self, playlist):

        dialog = PlaylistDialog(
            playlist.entries,
            self.playlist_selected,
        )

        dialog.open()


    def playlist_selected(self, videos):

        app = App.get_running_app()

        queue = app.sm.get_screen("queue")

        for video in videos:

            item = self.factory.build(
                url=video["url"],
                title=video["title"],
                playlist=PlaylistMetadata(),
            )

            if item is None:
                continue

            self.coordinator.add(item)

            queue.add_download(
                item.id,
                item.title,
                {
                    "pause": self.coordinator.pause,
                    "resume": self.coordinator.resume,
                    "cancel": self.coordinator.cancel,
                },
            )

    def update_ui(self, metadata):

        self.video_card.set_title(metadata.title)

        self.video_card.set_channel(metadata.channel)

        self.video_card.set_details(
            f"{format_duration(metadata.duration)} • {format_number(metadata.views)} views"
        )

        if metadata.thumbnail:
            self.video_card.set_thumbnail(metadata.thumbnail)

        self.download_panel.load_metadata(metadata)
        self.url_bar.url_input.error = False
        self.url_bar.url_input.helper_text = ""

    def download(self, *args):
        if self.metadata is None:
            return

        self.notifications.show(
            "YouTube Downloader",
            "Download started",
        )

        item = self.factory.build(
            self.url_bar.url_input.text.strip(),
            self.metadata.title,
            PlaylistMetadata(),
        )

        if item is None:
            return

        self.coordinator.add(item)

        app = App.get_running_app()

        queue = app.sm.get_screen("queue")

        self.queue_card = queue.add_download(
            item.id,
            item.title,
            {
                "pause": self.coordinator.pause,
                "resume": self.coordinator.resume,
                "cancel": self.coordinator.cancel,
            },
        )

    # ---------------- Progress ----------------

    def update_progress(self, value):

        Clock.schedule_once(
            lambda dt: (
                self.download_panel.set_progress(value),
                self.queue_card.update_progress(value),
            )
        )

    def update_status(self, text):
        Clock.schedule_once(
            lambda dt: (
                self.download_panel.set_status(text),
                self.queue_card.update_status(text),
            )
        )

    def download_completed(self, *args):

        self.notifications.show(
            "Download Complete",
            self.metadata.title,
        )

        app = App.get_running_app()

        history = app.sm.get_screen("history")

        history.add_history(self.metadata.title)

        Clock.schedule_once(
            lambda dt: (
                self.download_panel.finish(),
                self.queue_card.update_progress(100),
                self.queue_card.update_status("Completed"),
            )
        )

    def download_failed(self, *args):

        self.notifications.show(
            "Download Failed",
            self.metadata.title,
        )

        Clock.schedule_once(
            lambda dt: (
                self.download_panel.error(),
                self.queue_card.update_status("Failed"),
            )
        )
