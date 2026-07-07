from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateTimeEdit,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import QDateTime


def build_download_widget(window) -> QWidget:
    panel = QWidget()
    panel.setMinimumWidth(360)
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(12, 12, 12, 12)
    layout.setSpacing(12)

    form = QFormLayout()
    form.setLabelAlignment(form.labelAlignment())
    form.setFormAlignment(form.formAlignment())
    form.setHorizontalSpacing(16)
    form.setVerticalSpacing(10)

    window.type_box = QComboBox()
    window.type_box.addItems(["Video + Audio", "Video", "Audio"])
    window.preset_box = QComboBox()
    window.preset_box.addItems(
        [
            "Best Video",
            "1080p MP4",
            "720p MP4",
            "MP3 320",
            "MP3 128",
            "FLAC",
        ]
    )
    window.quality_box = QComboBox()
    window.quality_box.addItems(
        ["Best", "2160p", "1440p", "1080p", "720p", "480p", "360p", "240p", "144p"]
    )
    window.audio_bitrate_box = QComboBox()
    window.audio_bitrate_box.addItems(["320", "256", "192", "160", "128", "96", "64"])
    window.audio_codec_box = QComboBox()
    window.audio_codec_box.addItems(["mp3", "aac", "m4a", "flac", "wav", "ogg", "opus"])
    window.video_codec_box = QComboBox()
    window.video_codec_box.addItems(["h264", "best"])
    window.container_box = QComboBox()
    window.container_box.addItems(["mp4", "mkv", "webm", "mov"])
    window.subtitle_box = QComboBox()
    window.subtitle_box.addItem("None")
    window.embed_subs = QCheckBox("Embed subtitles")
    window.embed_metadata = QCheckBox("Embed metadata")
    window.embed_thumbnail = QCheckBox("Embed thumbnail")
    window.auto_subs = QCheckBox("Auto subtitles")
    window.translate_subs = QCheckBox("Translate subtitles")
    window.translation_lang = QComboBox()
    window.translation_lang.addItems(
        ["en", "es", "fr", "de", "pt", "ru", "ja", "ko", "zh-Hans"]
    )
    window.subtitle_format = QComboBox()
    window.subtitle_format.addItems(["srt", "vtt", "ass"])
    window.playlist_box = QComboBox()
    window.playlist_box.addItems(["Single video", "Entire playlist", "Selected videos"])
    window.schedule_enabled = QCheckBox("Schedule")
    window.schedule_time = QDateTimeEdit(QDateTime.currentDateTime())
    window.schedule_time.setCalendarPopup(True)
    window.schedule_time.setDisplayFormat("yyyy-MM-dd HH:mm")
    window.schedule_time.setMinimumDateTime(QDateTime.currentDateTime())
    window.schedule_time.setEnabled(False)
    window.filename_input = QLineEdit(window.settings.get("filename_template"))
    window.filename_input.setPlaceholderText("%(title)s.%(ext)s")
    window.folder_input = QLineEdit(window.settings.get("download_folder"))
    browse_btn = QPushButton("Browse")
    browse_btn.clicked.connect(window.select_folder)
    folder_row = QHBoxLayout()
    folder_row.addWidget(window.folder_input, 1)
    folder_row.addWidget(browse_btn)

    form.addRow("Preset", window.preset_box)
    form.addRow("Download type", window.type_box)
    form.addRow("Quality", window.quality_box)
    form.addRow("Audio bitrate", window.audio_bitrate_box)
    form.addRow("Audio codec", window.audio_codec_box)
    form.addRow("Video codec", window.video_codec_box)
    form.addRow("Container", window.container_box)
    form.addRow("Subtitle", window.subtitle_box)
    form.addRow("", window.embed_subs)
    form.addRow("", window.auto_subs)
    form.addRow("", window.translate_subs)
    form.addRow("Translation", window.translation_lang)
    form.addRow("Subtitle format", window.subtitle_format)
    form.addRow("", window.embed_metadata)
    form.addRow("", window.embed_thumbnail)
    form.addRow("Playlist", window.playlist_box)
    form.addRow("", window.schedule_enabled)
    form.addRow("Start at", window.schedule_time)
    form.addRow("Filename", window.filename_input)
    form.addRow("Save folder", folder_row)

    layout.addLayout(form)
    window.download_btn = QPushButton("Download")
    window.download_btn.setMinimumHeight(44)
    window.download_btn.clicked.connect(window.download)
    layout.addWidget(window.download_btn)
    layout.addStretch(1)

    def _update_fields() -> None:
        kind = window.type_box.currentText()
        is_audio_only = kind == "Audio"
        is_video_only = kind == "Video"
        window.video_codec_box.setEnabled(not is_audio_only)
        window.audio_codec_box.setEnabled(not is_video_only)
        window.audio_bitrate_box.setEnabled(not is_video_only)
        window.embed_thumbnail.setEnabled(not is_video_only)
        window.embed_metadata.setEnabled(True)
        window.embed_subs.setEnabled(True)
        window.auto_subs.setEnabled(True)
        window.translate_subs.setEnabled(window.subtitle_box.currentText() != "None")
        window.translation_lang.setEnabled(window.translate_subs.isChecked())
        window.subtitle_format.setEnabled(window.subtitle_box.currentText() != "None")
        window.schedule_time.setEnabled(window.schedule_enabled.isChecked())

    window.type_box.currentTextChanged.connect(lambda _: _update_fields())
    window.subtitle_box.currentTextChanged.connect(lambda _: _update_fields())
    window.translate_subs.stateChanged.connect(lambda _: _update_fields())
    window.schedule_enabled.toggled.connect(lambda _: _update_fields())
    _update_fields()

    container = QScrollArea()
    container.setWidgetResizable(True)
    container.setWidget(panel)
    return container
