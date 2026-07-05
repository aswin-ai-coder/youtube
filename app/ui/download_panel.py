from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
)


class DownloadPanel(QFrame):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("Download Options")
        title.setStyleSheet("""
            font-size:20px;
            font-weight:bold;
        """)

        layout.addWidget(title)

        group = QGroupBox()

        grid = QGridLayout()

        # -------------------------
        # Download Type
        # -------------------------

        self.video_radio = QRadioButton("Video")

        self.audio_radio = QRadioButton("Audio (MP3)")

        self.video_radio.setChecked(True)

        type_layout = QHBoxLayout()

        type_layout.addWidget(self.video_radio)

        type_layout.addWidget(self.audio_radio)

        grid.addWidget(QLabel("Download Type"), 0, 0)

        grid.addLayout(type_layout, 0, 1)

        # -------------------------
        # Quality
        # -------------------------

        self.quality_box = QComboBox()

        self.quality_box.addItems([
            "Best",
            "2160p",
            "1440p",
            "1080p",
            "720p",
            "480p",
            "360p",
        ])

        grid.addWidget(QLabel("Quality"), 1, 0)

        grid.addWidget(self.quality_box, 1, 1)

        # -------------------------
        # Folder
        # -------------------------

        self.folder_input = QLineEdit()

        self.folder_input.setText(
            str(Path.home() / "Downloads")
        )

        self.browse_btn = QPushButton("Browse")

        folder_layout = QHBoxLayout()

        folder_layout.addWidget(self.folder_input)

        folder_layout.addWidget(self.browse_btn)

        grid.addWidget(QLabel("Save Folder"), 2, 0)

        grid.addLayout(folder_layout, 2, 1)

        group.setLayout(grid)

        layout.addWidget(group)

        # -------------------------
        # Download Button
        # -------------------------

        self.download_btn = QPushButton("⬇ Download")

        self.download_btn.setMinimumHeight(50)

        layout.addWidget(self.download_btn)
