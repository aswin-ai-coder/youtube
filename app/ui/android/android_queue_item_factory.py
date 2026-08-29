from pathlib import Path

from app.core.models import DownloadKind
from app.core.queue_service import QueueItem
from app.core.playlist_service import PlaylistMetadata


class AndroidQueueItemFactory:

    def __init__(self, screen):
        self.screen = screen

    def build(
        self,
        url,
        title,
        playlist=PlaylistMetadata(),
    ):

        panel = self.screen.download_panel

        kind_map = {
            "Video": DownloadKind.VIDEO,
            "Audio": DownloadKind.AUDIO,
            "Video+Audio": DownloadKind.VIDEO_AUDIO,
        }

        settings = self.screen.settings

        output_dir = settings.get(
            "download_directory",
            str(Path.home() / "Downloads"),
        )

        return QueueItem(
            url=url,
            title=title,
            output_dir=output_dir,
            kind=kind_map.get(
                panel.selected_type(),
                DownloadKind.VIDEO_AUDIO,
            ),
            quality=panel.selected_quality(),
            audio_codec=settings.get(
                "audio_codec",
                "mp3",
            ),
            audio_bitrate=settings.get(
                "audio_bitrate",
                "320",
            ),
            video_codec=settings.get(
                "video_codec",
                "h264",
            ),
            container=settings.get(
                "container",
                "mp4",
            ),
            filename_template=settings.get(
                "filename_template",
                "%(title)s.%(ext)s",
            ),
            write_subtitles=panel.subtitles_enabled(),
            embed_thumbnail=True,
            embed_metadata=True,
            playlist=False,
            playlist_items=[],
        )
