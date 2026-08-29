from threading import Thread
from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from app.core.playlist_service import PlaylistService
from app.ui.android.widgets.playlist_dialog import PlaylistDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from app.core.youtube_service import YouTubeService
from app.core.queue_service import QueueService
from app.core.settings_service import SettingsService
from app.core.playlist_service import PlaylistMetadata
from app.core.notification_service import NotificationService
from app.ui.desktop.download_coordinator import DownloadCoordinator
from app.ui.android.android_queue_item_factory import AndroidQueueItemFactory
from app.ui.android.widgets.playlist_progress import PlaylistProgress
from app.utils.helpers import format_duration, format_number
from app.core.search_history_service import SearchHistoryService
from app.ui.android.widgets.url_bar import UrlBar
from app.ui.android.widgets.video_card import VideoCard
from app.ui.android.widgets.download_panel import DownloadPanel
from app.core.clipboard_service import ClipboardService
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogContentContainer,
)
from app.core.favorites_service import FavoritesService
from kivymd.uix.button import (
    MDButton,
    MDButtonText,
)
from app.core.background_download_manager import BackgroundDownloadManager


class HomeScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.youtube = YouTubeService()
        self.playlists = PlaylistService()
        self.settings = SettingsService()
        self.notifications = NotificationService()
        self.queue = QueueService()
        self.search_history = SearchHistoryService()
        self.coordinator = DownloadCoordinator(
            self.queue,
            self.settings,
            None,
        )
        self.favorites = FavoritesService()
        self.download_manager = BackgroundDownloadManager(
            self.coordinator
        )
        self.clipboard = ClipboardService(
            self.clipboard_detected
        )

        self.factory = AndroidQueueItemFactory(self)

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
        self.video_card.favorite_button.bind(on_release=self.favorite_video)
        self.download_panel = DownloadPanel()

        self.playlist_progress = PlaylistProgress()

        self.playlist_progress.opacity = 0

        self.url_bar.analyze_button.bind(
            on_release=self.analyze
        )

        self.download_panel.download_button.bind(
            on_release=self.download
        )

        content.add_widget(self.url_bar)
        content.add_widget(self.video_card)
        content.add_widget(self.download_panel)
        content.add_widget(self.playlist_progress)

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
        self.coordinator.speed_changed.connect(
            self.update_speed
        )

        self.coordinator.size_changed.connect(
            self.update_size
        )

        self.coordinator.eta_changed.connect(
            self.update_eta
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

        self.playlist_total = len(videos)

        self.playlist_current = 0

        self.playlist_progress.opacity = 1

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

            self.download_manager.add(item)

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
        self.search_history.add(
            self.url_bar.url_input.text.strip(),
            metadata.title,
        )
        self.url_bar.url_input.error = False
        self.url_bar.url_input.helper_text = ""

    def download(self, *args):
        if self.metadata is None:
            return
        item = self.factory.build(
            url=self.url_bar.url_input.text.strip(),
            title=self.metadata.title,
            playlist=PlaylistMetadata(),
            write_subtitles=self.download_panel.subtitles_enabled(),
        )

        if item is None:
            return

        self.notifications.show(
            "Downloading",
            item.title,
        )

        self.download_manager.add(item)

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
        if hasattr(self, "playlist_total"):
            self.playlist_current += 1

            self.playlist_progress.update(

                self.playlist_current,

                self.playlist_total,

            )

            if self.playlist_current == self.playlist_total:

                self.playlist_progress.opacity = 0

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
    def update_speed(self, speed):

        Clock.schedule_once(
            lambda dt: self.download_panel.set_speed(speed)
        )

    def update_size(self, downloaded, total):

        Clock.schedule_once(
            lambda dt: self.download_panel.set_size(
                downloaded,
                total,
            )
        )

    def update_eta(self, eta):

        Clock.schedule_once(
            lambda dt: self.download_panel.set_eta(eta)
        )

    def clipboard_detected(self, url):
        Clock.schedule_once(
            lambda dt: self.show_clipboard_dialog(url)
        )

    def show_clipboard_dialog(self, url):
        dialog = MDDialog(

            MDDialogHeadlineText(
                text="YouTube Link Detected",
            ),

            MDDialogContentContainer(

                MDButton(
                    MDButtonText(
                        text="Analyze",
                    ),
                    on_release=lambda x: (
                        setattr(
                            self.url_bar.url_input,
                            "text",
                            url,
                        ),
                        dialog.dismiss(),
                        self.analyze(),
                    ),
                ),

                MDButton(
                    MDButtonText(
                        text="Ignore",
                    ),
                    on_release=lambda x: dialog.dismiss(),
                ),

                orientation="vertical",
            ),
        )

        dialog.open()

    def favorite_video(self, *args):
        if self.metadata is None:
            return

        self.favorites.add(
            self.url_bar.url_input.text.strip(),
            self.metadata.title,
            self.metadata.thumbnail or "",
        )

        self.video_card.favorite_button.icon = "heart"
