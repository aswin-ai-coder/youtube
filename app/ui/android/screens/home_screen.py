from threading import Thread

from kivy.clock import Clock
from kivy.metrics import dp

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView

from app.core.youtube_service import YouTubeService
from app.core.queue_service import QueueService
from app.core.settings_service import SettingsService
from app.core.playlist_service import PlaylistMetadata

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

        self.settings = SettingsService()

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

        item = self.factory.build(
            self.url_bar.url_input.text.strip(),
            self.metadata.title,
            PlaylistMetadata(),
        )

        if item is None:
            return

        self.coordinator.add(item)

    # ---------------- Progress ----------------

    def update_progress(self, value):

        Clock.schedule_once(
            lambda dt: self.download_panel.set_progress(value)
        )

    def update_status(self, text):

        Clock.schedule_once(
            lambda dt: self.download_panel.set_status(text)
        )

    def download_completed(self, *args):

        Clock.schedule_once(
            lambda dt: self.download_panel.finish()
        )

    def download_failed(self, *args):

        Clock.schedule_once(
            lambda dt: self.download_panel.error()
        )
