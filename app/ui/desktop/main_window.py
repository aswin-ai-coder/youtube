from __future__ import annotations

from PySide6.QtCore import QByteArray, Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLineEdit,
    QScrollArea,
)
from PySide6.QtWidgets import QMainWindow, QMessageBox, QPlainTextEdit, QProgressBar
from PySide6.QtWidgets import QPushButton, QSplitter, QTabWidget, QVBoxLayout, QWidget
from app.utils.error_handler import ErrorHandler
from app.core.history_service import HistoryService
from app.core.playlist_service import PlaylistMetadata, PlaylistService
from app.core.queue_service import QueueService
from app.core.settings_service import SettingsService
from app.core.update_service import UpdateService
from app.core.youtube_service import YouTubeService
from app.ui.desktop.batch_dialog import BatchUrlDialog
from app.ui.desktop.clipboard_monitor import ClipboardMonitor
from app.ui.desktop.download_coordinator import DownloadCoordinator
from app.ui.desktop.download_options_panel import build_download_widget
from app.ui.desktop.history_actions import HistoryActions
from app.ui.desktop.history_panel import HistoryPanel
from app.ui.desktop.notifications import NotificationService
from app.ui.desktop.queue_item_factory import QueueItemFactory
from app.ui.desktop.queue_panel import QueuePanel
from app.ui.desktop.settings_dialog import SettingsDialog
from app.ui.desktop.theme import apply_desktop_theme
from app.ui.desktop.video_panel import VideoPanel
from app.utils.helpers import download_thumbnail, format_duration, format_number
from app.utils.validators import is_supported_url


class MainWindow(QMainWindow):
    """Desktop application shell."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("YouTube Downloader")
        self.setMinimumSize(1080, 740)
        self.youtube_service = YouTubeService()
        self.playlist_service = PlaylistService()
        self.settings = SettingsService()
        self.history = HistoryService()
        self.queue_service = QueueService()
        self.coordinator = DownloadCoordinator(self.queue_service, self.settings, self)
        self.history_actions = HistoryActions(self.history)
        self.queue_item_factory = QueueItemFactory(self)
        self.notifications = NotificationService(self)
        self.current_title = "Downloaded media"
        self.current_playlist = PlaylistMetadata()
        self._build_ui()
        self._connect_queue()
        self._load_window_state()
        self._load_history()
        self._apply_theme()
        self._start_clipboard_monitor()

    def _build_ui(self) -> None:
        self._build_actions()
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(16, 14, 16, 12)
        input_row = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(
            "Paste YouTube video, playlist, channel, or short URL"
        )
        self.url_input.returnPressed.connect(self.analyze)
        input_row.addWidget(self.url_input, 1)
        self.analyze_btn = QPushButton("Analyze")
        self.analyze_btn.clicked.connect(self.analyze)
        input_row.addWidget(self.analyze_btn)
        self.paste_btn = QPushButton("Paste")
        self.paste_btn.clicked.connect(self.paste_from_clipboard)
        input_row.addWidget(self.paste_btn)
        layout.addLayout(input_row)
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.video_panel = VideoPanel()
        video_scroll = QScrollArea()
        video_scroll.setWidgetResizable(True)
        video_scroll.setWidget(self.video_panel)
        self.main_splitter.addWidget(video_scroll)
        self.main_splitter.addWidget(build_download_widget(self))
        self.main_splitter.setStretchFactor(0, 3)
        self.main_splitter.setStretchFactor(1, 2)
        layout.addWidget(self.main_splitter, 2)
        self.bottom_tabs = QTabWidget()
        self.queue_panel = QueuePanel()
        self.history_panel = HistoryPanel()
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.bottom_tabs.addTab(self.queue_panel, "Queue")
        self.bottom_tabs.addTab(self.history_panel, "History")
        self.bottom_tabs.addTab(self.log_view, "Download Log")
        layout.addWidget(self.bottom_tabs, 1)
        self.setCentralWidget(root)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(220)
        self.statusBar().addPermanentWidget(self.progress_bar)
        self.statusBar().showMessage("Ready")
        self.setAcceptDrops(True)

    def _build_actions(self) -> None:
        toolbar = self.addToolBar("Main")
        toolbar.setMovable(False)
        toolbar.addAction("Analyze", self.analyze)
        toolbar.addAction("Download", self.download)
        toolbar.addAction("Batch", self.add_batch_urls)
        toolbar.addAction("Settings", self.open_settings)
        file_menu = self.menuBar().addMenu("File")
        file_menu.addAction("Download", self.download)
        file_menu.addAction("Add Batch URLs", self.add_batch_urls)
        file_menu.addAction("Settings", self.open_settings)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)
        tools_menu = self.menuBar().addMenu("Tools")
        tools_menu.addAction("Check for Updates", self.check_updates)
        tools_menu.addAction("Open Download Folder", self.open_download_folder)
        self.menuBar().addMenu("View").addAction("Refresh History", self._load_history)

    def _connect_queue(self) -> None:
        self.coordinator.queue_changed.connect(self._refresh_queue)
        self.coordinator.progress_changed.connect(self.progress_bar.setValue)
        self.coordinator.status_changed.connect(self.statusBar().showMessage)
        self.coordinator.completed.connect(self._download_finished)
        self.coordinator.failed.connect(self._download_failed)
        self.queue_panel.pause_requested.connect(self.coordinator.pause)
        self.queue_panel.resume_requested.connect(self.coordinator.resume)
        self.queue_panel.cancel_requested.connect(self.coordinator.cancel)
        self.queue_panel.retry_requested.connect(self.coordinator.retry)
        self.queue_panel.remove_requested.connect(self.coordinator.remove)
        self.queue_panel.move_requested.connect(self.coordinator.move)
        self.history_panel.refresh_requested.connect(self._load_history)
        self.history_panel.open_file_requested.connect(self.open_history_file)
        self.history_panel.open_folder_requested.connect(self.open_history_folder)
        self.history_panel.copy_url_requested.connect(self.copy_history_url)
        self.history_panel.delete_requested.connect(self.delete_history_item)

    def analyze(self) -> None:
        url = self.url_input.text().strip()
        if not is_supported_url(url):
            QMessageBox.warning(
                self, "Invalid URL", "Please enter a supported YouTube URL."
            )
            return
        try:
            self.statusBar().showMessage("Analyzing...")
            self.current_playlist = self.playlist_service.get_playlist_info(url)
            metadata = self.youtube_service.get_video_info(url)
            metadata.playlist_count = (
                metadata.playlist_count or self.current_playlist.count
            )
            if metadata.is_live:
                QMessageBox.warning(
                    self,
                    "Livestream",
                    "Live streams can be downloaded after YouTube publishes the completed recording.",
                )
            self.current_title = metadata.title or "Downloaded media"
            self.video_panel.set_info(
                metadata.title or "-",
                metadata.channel or "-",
                format_duration(metadata.duration),
                format_number(metadata.views),
                metadata.upload_date or "-",
                video_id=metadata.video_id or "-",
                description=metadata.description or "-",
                playlist_count=metadata.playlist_count,
                resolution=metadata.best_resolution,
                fps=metadata.best_fps,
                video_codec=metadata.best_video_codec,
                audio_codec=metadata.best_audio_codec,
                bitrate=metadata.best_bitrate,
                hdr=metadata.is_hdr,
                comments=metadata.comment_count,
            )
            if metadata.thumbnail and (
                pixmap := download_thumbnail(metadata.thumbnail)
            ):
                self.video_panel.set_thumbnail(pixmap)
            self.quality_box.clear()
            self.quality_box.addItems(["Best", *metadata.qualities])
            self.subtitle_box.clear()
            self.subtitle_box.addItem("None")
            self.subtitle_box.addItems([track.language for track in metadata.subtitles])
            self._log(
                "Playlist detected"
                if self.current_playlist.is_playlist
                else "Analysis complete"
            )
            self.statusBar().showMessage("Ready")
        except Exception as exc:
            message = ErrorHandler.handle(
                exc,
                context="Analyze video",
            )

            QMessageBox.critical(
                self,
                "Analysis failed",
                message,
            )

            self.statusBar().showMessage("Analysis failed")

    def download(self) -> None:
        url = self.url_input.text().strip()
        if not is_supported_url(url):
            QMessageBox.warning(
                self, "Invalid URL", "Please enter a supported YouTube URL."
            )
            return
        item = self.queue_item_factory.build(
            url, self.current_title, self.current_playlist
        )
        if item is None:
            return
        self.coordinator.add(item)
        self._log(f"Queued: {item.title or item.url}")

    def add_batch_urls(self) -> None:
        dialog = BatchUrlDialog(self)
        if dialog.exec() != 1:
            return
        for url in dialog.urls():
            item = self.queue_item_factory.build(
                url,
                url,
                PlaylistMetadata(),
                allow_playlist_prompt=False,
                force_playlist=False,
            )
            if item:
                self.coordinator.add(item)

    def _download_finished(self, item_id: str, output_dir: str) -> None:
        item = self.queue_service.get(item_id)
        title = item.title if item else self.current_title
        url = item.url if item else self.url_input.text().strip()
        self.history.add_record(
            title=title or "Downloaded media",
            url=url,
            output_path=output_dir,
            status="completed",
        )
        self._load_history()
        self._log(f"Completed: {title}")
        self.notifications.show("Download completed", title or "Download completed")

    def _download_failed(self, item_id: str, message: str) -> None:
        item = self.queue_service.get(item_id)
        title = item.title if item else self.current_title
        url = item.url if item else self.url_input.text().strip()
        self.history.add_record(
            title=title or "Failed download", url=url, status="failed"
        )
        self._load_history()
        self._log(f"Failed: {message}")
        self.notifications.show("Download failed", message)

    def _refresh_queue(self) -> None:
        self.queue_panel.set_queue_items(self.queue_service.list_items())

    def _load_history(self, query: str = "", status: str = "") -> None:
        self.history_panel.set_records(
            self.history.search(query=query, status=status or None, limit=100)
        )

    def paste_from_clipboard(self) -> None:
        text = QApplication.clipboard().text().strip()
        if text:
            self.url_input.setText(text.splitlines()[0])

    def select_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(
            self, "Choose download folder", self.folder_input.text()
        )
        if folder:
            self.folder_input.setText(folder)

    def open_settings(self) -> None:
        dialog = SettingsDialog(self.settings.as_dict())
        if dialog.exec() == 1:
            self.settings.update(dialog.values())
            self.settings.save()
            self.folder_input.setText(self.settings.get("download_folder"))
            self.filename_input.setText(self.settings.get("filename_template"))
            self._apply_theme()

    def check_updates(self) -> None:
        try:
            status = UpdateService().check()
            text = f"yt-dlp {status.current_version} is current."
            if status.update_available:
                text = f"yt-dlp {status.latest_version} is available."
            QMessageBox.information(self, "Update Check", text)
        except Exception as exc:
            message = ErrorHandler.handle(
                exc,
                context="Update check",
            )

            QMessageBox.warning(
                self,
                "Update Check Failed",
                message,
            )

    def open_download_folder(self) -> None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.folder_input.text()))

    def open_history_file(self, record_id: int) -> None:
        self.history_actions.open_file(record_id)

    def open_history_folder(self, record_id: int) -> None:
        self.history_actions.open_folder(record_id)

    def copy_history_url(self, record_id: int) -> None:
        self.history_actions.copy_url(record_id)

    def delete_history_item(self, record_id: int) -> None:
        self.history.delete(record_id)
        self._load_history()

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:
        text = event.mimeData().text().strip()
        if text:
            self.url_input.setText(text.splitlines()[0])
            event.acceptProposedAction()

    def closeEvent(self, event) -> None:
        self.coordinator.shutdown()

        self.settings.set(
            "window_geometry",
            bytes(self.saveGeometry().toBase64()).decode(),
        )

        self.settings.set(
            "splitter_sizes",
            self.main_splitter.sizes(),
        )

        self.settings.save()

        super().closeEvent(event)

    def _start_clipboard_monitor(self) -> None:
        self.clipboard_monitor = ClipboardMonitor(self)
        self.clipboard_monitor.url_detected.connect(self._clipboard_url_detected)

    def _clipboard_url_detected(self, url: str) -> None:
        self.url_input.setText(url)
        self.statusBar().showMessage("YouTube URL detected on clipboard")

    def _load_window_state(self) -> None:
        geometry = self.settings.get("window_geometry")
        if geometry:
            self.restoreGeometry(QByteArray.fromBase64(geometry.encode()))
        if sizes := self.settings.get("splitter_sizes", []):
            self.main_splitter.setSizes([int(size) for size in sizes])

    def _apply_theme(self) -> None:
        apply_desktop_theme(self, self.settings.as_dict())

    def _log(self, message: str) -> None:
        self.log_view.appendPlainText(message)
