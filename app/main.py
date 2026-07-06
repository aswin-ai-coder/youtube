import sys

from PySide6.QtWidgets import QApplication

from app.ui.desktop.main_window import MainWindow
from app.utils.logger import get_logger


logger = get_logger()


def main() -> None:
    logger.info("========== Application Started ==========")

    app = QApplication(sys.argv)
    app.setApplicationName("YouTube Downloader")

    window = MainWindow()
    window.show()

    exit_code = app.exec()

    logger.info("========== Application Closed ==========")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
