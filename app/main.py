import sys

from PySide6.QtWidgets import QApplication

from ui.desktop.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("YouTube Downloader")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
