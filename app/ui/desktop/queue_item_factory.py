from __future__ import annotations

from app.core.models import DownloadKind
from app.core.playlist_service import PlaylistMetadata
from app.core.queue_service import QueueItem
from app.ui.desktop.playlist_dialog import PlaylistSelectionDialog


class QueueItemFactory:
    def __init__(self, window) -> None:
        self.window = window

    def build(
        self,
        url: str,
        title: str,
        playlist: PlaylistMetadata,
        allow_playlist_prompt: bool = True,
        force_playlist: bool | None = None,
        write_subtitles: bool | None = None,
    ) -> QueueItem | None:
        scheduled_at = None
        if self.window.schedule_enabled.isChecked():
            scheduled_at = self.window.schedule_time.dateTime().toPython()
        playlist_enabled = (
            force_playlist
            if force_playlist is not None
            else self.window.playlist_box.currentText() != "Single video"
        )
        return QueueItem(
            url=url,
            output_dir=self.window.folder_input.text(),
            title=title,
            quality=self.window.quality_box.currentText(),
            kind=self._kind(),
            audio_codec=self.window.audio_codec_box.currentText(),
            audio_bitrate=self.window.audio_bitrate_box.currentText(),
            video_codec=self.window.video_codec_box.currentText(),
            container=self.window.container_box.currentText(),
            filename_template=self.window.filename_input.text().strip()
            or "%(title)s.%(ext)s",
            subtitle_languages=self._subtitle_languages(),
            write_subtitles=(
                write_subtitles
                if write_subtitles is not None
                else bool(self._subtitle_languages())
            ),
            write_auto_subtitles=self.window.auto_subs.isChecked(),
            translate_subtitles=self.window.translate_subs.isChecked(),
            translation_language=self.window.translation_lang.currentText(),
            subtitle_format=self.window.subtitle_format.currentText(),
            embed_subtitles=self.window.embed_subs.isChecked(),
            playlist=playlist_enabled,
            playlist_items=(
                self._selected_playlist_items(playlist, allow_playlist_prompt)
                if playlist_enabled
                else []
            ),
            scheduled_at=scheduled_at,
        )

    def _kind(self) -> DownloadKind:
        kind_map = {
            "Video + Audio": DownloadKind.VIDEO_AUDIO,
            "Video": DownloadKind.VIDEO,
            "Audio": DownloadKind.AUDIO,
        }
        return kind_map[self.window.type_box.currentText()]

    def _subtitle_languages(self) -> list[str]:
        subtitle = self.window.subtitle_box.currentText()
        return [] if subtitle == "None" else [subtitle]

    def _selected_playlist_items(
        self, playlist: PlaylistMetadata, allow_prompt: bool
    ) -> list[str]:
        if self.window.playlist_box.currentText() != "Selected videos":
            return []
        entries = playlist.entries or []
        if not allow_prompt or not entries:
            return []
        dialog = PlaylistSelectionDialog(entries, self.window)
        if dialog.exec() != 1:
            return []
        return dialog.selected_indexes()
