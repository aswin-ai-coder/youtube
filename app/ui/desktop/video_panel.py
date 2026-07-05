from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QVBoxLayout,
)


class VideoPanel(QFrame):

    def __init__(self):
        super().__init__()

        self.setObjectName("videoPanel")

        layout = QVBoxLayout(self)

        title = QLabel("Video Information")
        title.setStyleSheet("""
            font-size:20px;
            font-weight:bold;
        """)

        layout.addWidget(title)

        grid = QGridLayout()

        self.thumbnail = QLabel()

        self.thumbnail.setFixedSize(360, 220)

        self.thumbnail.setAlignment(Qt.AlignCenter)

        self.thumbnail.setStyleSheet("""

            background:#2f2f2f;

            border-radius:10px;

            border:2px solid #555;

        """)

        self.thumbnail.setText("Thumbnail")

        grid.addWidget(self.thumbnail, 0, 0, 6, 1)

        self.title = QLabel("Title : -")
        self.channel = QLabel("Channel : -")
        self.duration = QLabel("Duration : -")
        self.views = QLabel("Views : -")
        self.upload = QLabel("Upload Date : -")
        self.resolution = QLabel("Resolution : -")
        self.fps = QLabel("FPS : -")
        self.video_codec = QLabel("Video codec : -")
        self.audio_codec = QLabel("Audio codec : -")
        self.bitrate = QLabel("Bitrate : -")
        self.hdr = QLabel("HDR : -")
        self.comments = QLabel("Comments : -")
        self.playlist = QLabel("Playlist Count : -")
        self.id_label = QLabel("Video ID : -")
        self.description = QLabel("Description : -")

        self.title.setWordWrap(True)
        self.description.setWordWrap(True)

        grid.addWidget(self.title, 0, 1)

        grid.addWidget(self.channel, 1, 1)

        grid.addWidget(self.duration, 2, 1)

        grid.addWidget(self.views, 3, 1)

        grid.addWidget(self.upload, 4, 1)
        grid.addWidget(self.resolution, 5, 1)
        grid.addWidget(self.fps, 6, 1)
        grid.addWidget(self.video_codec, 7, 1)
        grid.addWidget(self.audio_codec, 8, 1)
        grid.addWidget(self.bitrate, 9, 1)
        grid.addWidget(self.hdr, 10, 1)
        grid.addWidget(self.comments, 11, 1)
        grid.addWidget(self.playlist, 12, 1)
        grid.addWidget(self.id_label, 13, 1)
        grid.addWidget(self.description, 14, 1)

        layout.addLayout(grid)

    def clear(self):
        self.thumbnail.clear()
        self.thumbnail.setText("Thumbnail")
        self.title.setText("Title : -")
        self.channel.setText("Channel : -")
        self.duration.setText("Duration : -")
        self.views.setText("Views : -")
        self.upload.setText("Upload Date : -")
        self.resolution.setText("Resolution : -")
        self.fps.setText("FPS : -")
        self.video_codec.setText("Video codec : -")
        self.audio_codec.setText("Audio codec : -")
        self.bitrate.setText("Bitrate : -")
        self.hdr.setText("HDR : -")
        self.comments.setText("Comments : -")
        self.playlist.setText("Playlist Count : -")
        self.id_label.setText("Video ID : -")
        self.description.setText("Description : -")

    def set_info(
        self,
        title,
        channel,
        duration,
        views,
        upload,
        video_id=None,
        description=None,
        playlist_count=None,
        resolution=None,
        fps=None,
        video_codec=None,
        audio_codec=None,
        bitrate=None,
        hdr=False,
        comments=None,
    ):
        self.title.setText(f"Title : {title}")
        self.channel.setText(f"Channel : {channel}")
        self.duration.setText(f"Duration : {duration}")
        self.views.setText(f"Views : {views}")
        self.upload.setText(f"Upload Date : {upload}")
        self.resolution.setText(f"Resolution : {resolution or '-'}")
        self.fps.setText(f"FPS : {fps or '-'}")
        self.video_codec.setText(f"Video codec : {video_codec or '-'}")
        self.audio_codec.setText(f"Audio codec : {audio_codec or '-'}")
        self.bitrate.setText(f"Bitrate : {bitrate or '-'}")
        self.hdr.setText(f"HDR : {'Yes' if hdr else 'No'}")
        self.comments.setText(f"Comments : {comments or '-'}")
        self.playlist.setText(f"Playlist Count : {playlist_count or '-'}")
        self.id_label.setText(f"Video ID : {video_id or '-'}")
        self.description.setText(f"Description : {description or '-'}")

    def set_thumbnail(self, pixmap: QPixmap):

        self.thumbnail.setPixmap(
            pixmap.scaled(
                self.thumbnail.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )
