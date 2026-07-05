from __future__ import annotations

from PySide6.QtWidgets import QWidget


def apply_desktop_theme(widget: QWidget, settings: dict) -> None:
    light = settings.get("theme") == "light"
    bg = "#f6f7fb" if light else "#101318"
    panel = "#ffffff" if light else "#1b2029"
    text = "#111827" if light else "#f3f4f6"
    border = "#d1d5db" if light else "#2b3340"
    accent = settings.get("accent_color", "#2563eb")
    widget.setStyleSheet(f"""
        QWidget {{ background: {bg}; color: {text}; font-size: 13px; }}
        QMenuBar, QMenu, QStatusBar {{ background: {panel}; color: {text}; }}
        QLineEdit, QComboBox, QListWidget, QPlainTextEdit, QProgressBar {{
            background: {panel};
            border: 1px solid {border};
            border-radius: 8px;
            padding: 7px;
        }}
        QPushButton {{
            background: {accent};
            color: white;
            border: 0;
            border-radius: 10px;
            padding: 10px 14px;
            min-height: 36px;
        }}
        QPushButton:hover {{ background: #1d4ed8; }}
        QLineEdit:focus, QComboBox:focus, QListWidget:focus, QPlainTextEdit:focus {{
            border: 1px solid {accent};
            outline: none;
        }}
        QTabWidget::pane {{
            border: 1px solid {border};
            border-radius: 10px;
            padding: 8px;
            background: {panel};
        }}
        QTabBar::tab {{
            background: {panel};
            border: 1px solid {border};
            border-bottom: none;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            padding: 10px 16px;
            min-width: 100px;
        }}
        QTabBar::tab:selected {{
            background: {bg};
            border-bottom: 1px solid {bg};
        }}
        QStatusBar {{
            border-top: 1px solid {border};
            padding: 4px 10px;
        }}
        QLabel {{ background: transparent; }}
    """)
