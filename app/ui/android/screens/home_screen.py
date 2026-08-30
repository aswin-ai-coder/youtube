from __future__ import annotations

from threading import Thread

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView

from app.core.android_download_coordinator import AndroidDownloadCoordinator
from app.core.clipboard_service import ClipboardService
from app.core.favorites_service import FavoritesService
from app.core.history_service import HistoryService
from app.core.notification_service import NotificationService
from app.core.playlist_service import PlaylistMetadata, PlaylistService
from app.core.queue_service import QueueService
from app.core.search_history_service import SearchHistoryService
from app.core.settings_service import SettingsService
from app.core.youtube_service import YouTubeService
from app.ui.android.android_queue_item_factory import AndroidQueueItemFactory
from app.ui.android.widgets.download_panel import DownloadPanel
from app.ui.android.widgets.playlist_dialog import PlaylistDialog
from app.ui.android.widgets.playlist_progress import PlaylistProgress
from app.ui.android.widgets.url_bar import UrlBar
from app.ui.android.widgets.video_card import VideoCard
from app.utils.helpers import format_duration, format_number


class HomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.youtube = YouTubeService()
        self.playlists = PlaylistService()
        self.settings = SettingsService()
        self.queue = QueueService()
        self.history = HistoryService()
        self.search_history = SearchHistoryService()
        self.favorites = FavoritesService()
        self.notifications = NotificationService()
        self.coordinator = AndroidDownloadCoordinator(self.queue, self.settings)
        self.factory = AndroidQueueItemFactory(self)
        self.metadata = None
        self.queue_cards = {}
        self.playlist_total = 0
        self.playlist_current = 0

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
        self.playlist_progress = PlaylistProgress(opacity=0)

        self.video_card.favorite_button.bind(on_release=self.favorite_video)
        self.url_bar.analyze_button.bind(on_release=self.analyze)
        self.download_panel.download_button.bind(on_release=self.download)

        for widget in (
            self.url_bar,
            self.video_card,
            self.download_panel,
            self.playlist_progress,
        ):
            content.add_widget(widget)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

        self.coordinator.progress_changed.connect(self.update_progress)
        self.coordinator.status_changed.connect(self.update_status)
        self.coordinator.completed.connect(self.download_completed)
        self.coordinator.failed.connect(self.download_failed)
        self.coordinator.speed_changed.connect(self.update_speed)
        self.coordinator.size_changed.connect(self.update_size)
        self.coordinator.eta_changed.connect(self.update_eta)

        self.clipboard = None
        if self.settings.get("clipboard_monitor", True):
            self.clipboard = ClipboardService(self.clipboard_detected)

        # Resume queued/scheduled downloads after an app restart while the
        # Android activity is in the foreground and can legally start the FGS.
        if self.queue.due_count() > 0:
            Clock.schedule_once(lambda _dt: self.coordinator.start_available(), 0)

    def analyze(self, *args):
        url = self.url_bar.url_input.text.strip()
        if not url:
            return
        self.url_bar.set_loading(True)
        Thread(target=self._analyze_worker, args=(url,), daemon=True).start()

    def _analyze_worker(self, url):
        try:
            playlist = self.playlists.get_playlist_info(url)
            metadata = self.youtube.get_video_info(url)
            metadata.playlist_count = metadata.playlist_count or playlist.count
            Clock.schedule_once(lambda dt: self._show_metadata(metadata, playlist))
        except Exception as exc:
            Clock.schedule_once(lambda dt: self.url_bar.show_error(str(exc)))
        finally:
            Clock.schedule_once(lambda dt: self.url_bar.set_loading(False))

    def _show_metadata(self, metadata, playlist: PlaylistMetadata):
        self.metadata = metadata
        self.video_card.set_title(metadata.title or "Untitled")
        self.video_card.set_channel(metadata.channel or "Unknown channel")
        self.video_card.set_details(
            f"{format_duration(metadata.duration)} • "
            f"{format_number(metadata.views)} views"
        )
        if metadata.thumbnail:
            self.video_card.set_thumbnail(metadata.thumbnail)
        self.download_panel.load_metadata(metadata)
        self.search_history.add(
            self.url_bar.url_input.text.strip(),
            metadata.title or "Untitled",
        )
        self.url_bar.url_input.error = False
        self.url_bar.url_input.helper_text = ""
        if playlist.is_playlist:
            PlaylistDialog(
                playlist.entries or [],
                self.playlist_selected,
            ).open()

    def playlist_selected(self, videos):
        self.playlist_total = len(videos)
        self.playlist_current = 0
        self.playlist_progress.opacity = 1 if videos else 0

        for video in videos:
            item = self.factory.build(
                video["url"],
                video["title"],
            )
            self._enqueue(item)

    def download(self, *args):
        if self.metadata is None:
            return
        item = self.factory.build(
            self.url_bar.url_input.text.strip(),
            self.metadata.title or "Untitled",
            write_subtitles=self.download_panel.subtitles_enabled(),
        )
        self._enqueue(item)

    def _enqueue(self, item):
        if item is None:
            return

        queue_screen = App.get_running_app().sm.get_screen("queue")
        card = queue_screen.add_download(
            item.id,
            item.title or "Download",
            {
                "pause": self.coordinator.pause,
                "resume": self.coordinator.resume,
                "cancel": self.coordinator.cancel,
            },
        )
        self.queue_cards[item.id] = card

        self.coordinator.add(item)
        if self.settings.get("notifications", True):
            self.notifications.show(
                "Downloading",
                item.title or "Download",
            )

    def update_progress(self, item_id, value):
        Clock.schedule_once(
            lambda dt: self._card(item_id, "update_progress", value)
        )

    def update_status(self, item_id, text):
        Clock.schedule_once(
            lambda dt: self._card(item_id, "update_status", text)
        )

    def update_speed(self, item_id, speed):
        if item_id in self.queue_cards:
            Clock.schedule_once(
                lambda dt: self.download_panel.set_speed(speed)
            )

    def update_size(self, item_id, downloaded, total):
        if item_id in self.queue_cards:
            Clock.schedule_once(
                lambda dt: self.download_panel.set_size(downloaded, total)
            )

    def update_eta(self, item_id, eta):
        if item_id in self.queue_cards:
            Clock.schedule_once(
                lambda dt: self.download_panel.set_eta(eta)
            )

    def _card(self, item_id, method, value):
        card = self.queue_cards.get(item_id)
        if card is not None:
            getattr(card, method)(value)

    def _advance_playlist(self):
        if self.playlist_total <= 0:
            return
        self.playlist_current = min(
            self.playlist_current + 1,
            self.playlist_total,
        )
        self.playlist_progress.update(
            self.playlist_current,
            self.playlist_total,
        )
        if self.playlist_current >= self.playlist_total:
            self.playlist_progress.opacity = 0

    def download_completed(self, item_id, output_path):
        self._card(item_id, "update_progress", 100)
        self._card(item_id, "update_status", "Completed")
        self._advance_playlist()

    def download_failed(self, item_id, message):
        self._card(item_id, "update_status", "Failed")
        self._advance_playlist()

    def clipboard_detected(self, url):
        def apply_clipboard(_dt):
            self.url_bar.url_input.text = url

        Clock.schedule_once(apply_clipboard)

    def favorite_video(self, *args):
        if self.metadata is not None:
            self.favorites.add(
                self.url_bar.url_input.text.strip(),
                self.metadata.title or "Untitled",
                self.metadata.thumbnail or "",
            )
            self.video_card.favorite_button.icon = "heart"
