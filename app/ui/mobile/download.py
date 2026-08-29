from __future__ import annotations

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.textinput import TextInput

from app.core.favorites_service import FavoritesService
from app.core.models import DownloadKind
from app.core.queue_service import QueueItem
from app.core.settings_service import SettingsService
from app.core.youtube_service import YouTubeService
from app.ui.mobile.state import mobile_manager
from app.utils.validators import is_supported_url


class DownloadPage(TabbedPanelItem):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.settings = SettingsService()
        self.youtube = YouTubeService()
        self.favorites = FavoritesService()
        self.thumbnail_url = ""
        self.content = self._build()

    def _build(self) -> BoxLayout:
        layout = BoxLayout(orientation="vertical", padding=12, spacing=8)
        scroll = ScrollView(size_hint=(1, 1))
        form = BoxLayout(
            orientation="vertical", padding=8, spacing=10, size_hint_y=None
        )
        form.bind(minimum_height=form.setter("height"))

        self.url_input = TextInput(
            hint_text="YouTube URL", multiline=False, size_hint_y=None, height=44
        )
        self.title_label = Label(text="Ready", size_hint_y=None, height=54, text_size=(None, None))
        self.thumbnail = AsyncImage(source="", size_hint_y=None, height=180, allow_stretch=True, keep_ratio=True)
        self.type_spinner = Spinner(
            text="Video + Audio", values=["Video + Audio", "Video", "Audio"], size_hint_y=None, height=44
        )
        self.quality_spinner = Spinner(text="Best", values=["Best"], size_hint_y=None, height=44)
        self.bitrate_spinner = Spinner(text="320", values=["320", "256", "192", "160", "128", "96", "64"], size_hint_y=None, height=44)
        self.codec_spinner = Spinner(text="mp3", values=["mp3", "aac", "m4a", "flac", "wav", "ogg", "opus"], size_hint_y=None, height=44)
        self.container_spinner = Spinner(text="mp4", values=["mp4", "mkv", "webm", "mov"], size_hint_y=None, height=44)
        self.subtitle_spinner = Spinner(text="None", values=["None"], size_hint_y=None, height=44)
        self.auto_subs = CheckBox(active=False)
        self.translate_subs = CheckBox(active=False)
        self.translation_lang = Spinner(text="en", values=["en", "es", "fr", "de", "pt", "ru", "ja", "ko", "zh-Hans"], size_hint_y=None, height=44)
        self.subtitle_format = Spinner(text="srt", values=["srt", "vtt", "ass"], size_hint_y=None, height=44)
        self.playlist_spinner = Spinner(text="Single video", values=["Single video", "Entire playlist", "Selected videos"], size_hint_y=None, height=44)
        self.selected_videos_input = TextInput(hint_text="Indexes e.g. 1,3-5", multiline=False, disabled=True, size_hint_y=None, height=44)

        analyze_btn = Button(text="Analyze", size_hint_y=None, height=48)
        analyze_btn.bind(on_press=self.analyze)
        favorite_btn = Button(text="Add to Favorites", size_hint_y=None, height=44)
        favorite_btn.bind(on_press=self.toggle_favorite)
        self.favorite_btn = favorite_btn
        download_btn = Button(text="Download", size_hint_y=None, height=48)
        download_btn.bind(on_press=self.download)
        self.status_label = Label(text="", size_hint_y=None, height=32)

        for widget in (
            self.url_input,
            self.thumbnail,
            self.title_label,
            Label(text="Download type", size_hint_y=None, height=24),
            self.type_spinner,
            Label(text="Quality", size_hint_y=None, height=24),
            self.quality_spinner,
            Label(text="Audio bitrate", size_hint_y=None, height=24),
            self.bitrate_spinner,
            Label(text="Audio codec", size_hint_y=None, height=24),
            self.codec_spinner,
            Label(text="Container", size_hint_y=None, height=24),
            self.container_spinner,
            Label(text="Subtitle language", size_hint_y=None, height=24),
            self.subtitle_spinner,
        ):
            form.add_widget(widget)

        playlist_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=44)
        playlist_row.add_widget(Label(text="Playlist", size_hint_x=0.5))
        playlist_row.add_widget(self.playlist_spinner)
        form.add_widget(playlist_row)
        selected_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=44)
        selected_row.add_widget(Label(text="Selected video indexes", size_hint_x=0.5))
        selected_row.add_widget(self.selected_videos_input)
        form.add_widget(selected_row)

        autosub_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=34)
        autosub_row.add_widget(Label(text="Auto-subtitles", size_hint_x=0.7))
        autosub_row.add_widget(self.auto_subs)
        form.add_widget(autosub_row)
        translate_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=34)
        translate_row.add_widget(Label(text="Translate subtitles", size_hint_x=0.7))
        translate_row.add_widget(self.translate_subs)
        form.add_widget(translate_row)
        translation_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=44)
        translation_row.add_widget(Label(text="Target language", size_hint_x=0.5))
        translation_row.add_widget(self.translation_lang)
        form.add_widget(translation_row)
        format_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=44)
        format_row.add_widget(Label(text="Subtitle format", size_hint_x=0.5))
        format_row.add_widget(self.subtitle_format)
        form.add_widget(format_row)

        form.add_widget(analyze_btn)
        form.add_widget(favorite_btn)
        form.add_widget(download_btn)
        form.add_widget(self.status_label)

        self.subtitle_spinner.bind(text=self._update_subtitle_fields)
        self.translate_subs.bind(active=self._update_subtitle_fields)
        self.playlist_spinner.bind(text=self._update_playlist_fields)
        self._update_subtitle_fields()
        self._update_playlist_fields()
        scroll.add_widget(form)
        layout.add_widget(scroll)
        return layout

    def _parse_selection_indexes(self, text: str) -> list[str]:
        indexes: list[str] = []
        for part in text.split(","):
            item = part.strip()
            if not item:
                continue
            if "-" in item:
                try:
                    start, end = item.split("-", 1)
                    start_i, end_i = int(start), int(end)
                    if start_i > end_i:
                        continue
                    indexes.extend(str(i) for i in range(start_i, end_i + 1))
                except ValueError:
                    continue
            else:
                try:
                    value = int(item)
                    if value > 0:
                        indexes.append(str(value))
                except ValueError:
                    continue
        return list(dict.fromkeys(indexes))

    def _update_subtitle_fields(self, *_args) -> None:
        has_subtitles = self.subtitle_spinner.text != "None"
        self.translate_subs.disabled = not has_subtitles
        self.translation_lang.disabled = not (has_subtitles and self.translate_subs.active)
        self.subtitle_format.disabled = not has_subtitles

    def _update_playlist_fields(self, *_args) -> None:
        self.selected_videos_input.disabled = self.playlist_spinner.text != "Selected videos"

    def analyze(self, *_args) -> None:
        url = self.url_input.text.strip()
        if not is_supported_url(url):
            self.title_label.text = "Enter a supported YouTube URL"
            self.status_label.text = ""
            return
        self.status_label.text = "Analyzing..."
        try:
            metadata = self.youtube.get_video_info(url)
            self.title_label.text = metadata.title or "Untitled"
            self.thumbnail_url = metadata.thumbnail or ""
            self.thumbnail.source = self.thumbnail_url
            self.quality_spinner.values = ["Best", *metadata.qualities]
            self.quality_spinner.text = "Best"
            subtitle_values = ["None", *dict.fromkeys(track.language for track in metadata.subtitles)]
            self.subtitle_spinner.values = subtitle_values
            if self.subtitle_spinner.text not in subtitle_values:
                self.subtitle_spinner.text = "None"
            self._update_favorite_button(url)
            self.status_label.text = "Analysis complete"
        except Exception as exc:
            self.thumbnail.source = ""
            self.status_label.text = f"Analysis failed: {exc}"

    def toggle_favorite(self, *_args) -> None:
        url = self.url_input.text.strip()
        if not is_supported_url(url):
            return
        existing = {row[0] for row in self.favorites.all()}
        if url in existing:
            self.favorites.remove(url)
        else:
            self.favorites.add(url, self.title_label.text or url, self.thumbnail_url)
        self._update_favorite_button(url)

    def _update_favorite_button(self, url: str) -> None:
        try:
            favorite_urls = {row[0] for row in self.favorites.all()}
            self.favorite_btn.text = "Remove from Favorites" if url in favorite_urls else "Add to Favorites"
        except Exception:
            self.favorite_btn.text = "Add to Favorites"

    def download(self, *_args) -> None:
        url = self.url_input.text.strip()
        if not is_supported_url(url):
            self.status_label.text = "Enter a supported YouTube URL"
            return
        mobile_manager.enqueue(self._queue_item(url))
        self.status_label.text = "Queued for download"

    def _queue_item(self, url: str) -> QueueItem:
        kind_map = {
            "Video + Audio": DownloadKind.VIDEO_AUDIO,
            "Video": DownloadKind.VIDEO,
            "Audio": DownloadKind.AUDIO,
        }
        preferred_subtitles = [] if self.subtitle_spinner.text == "None" else [self.subtitle_spinner.text]
        playlist_items = self._parse_selection_indexes(self.selected_videos_input.text) if self.playlist_spinner.text == "Selected videos" else []
        return QueueItem(
            url=url,
            output_dir=self.settings.get("download_folder"),
            kind=kind_map[self.type_spinner.text],
            quality=self.quality_spinner.text,
            audio_codec=self.codec_spinner.text,
            audio_bitrate=self.bitrate_spinner.text,
            video_codec="h264",
            container=self.container_spinner.text,
            filename_template=self.settings.get("filename_template", "%(title)s.%(ext)s"),
            subtitle_languages=preferred_subtitles,
            write_subtitles=bool(preferred_subtitles),
            write_auto_subtitles=self.auto_subs.active,
            translate_subtitles=self.translate_subs.active,
            translation_language=self.translation_lang.text,
            subtitle_format=self.subtitle_format.text,
            embed_subtitles=False,
            embed_thumbnail=True,
            embed_metadata=True,
            thumbnail_url=self.thumbnail_url or None,
            playlist=self.playlist_spinner.text != "Single video",
            playlist_items=playlist_items,
            title=self.title_label.text,
        )
