from __future__ import annotations

import sqlite3
from pathlib import Path


class DatabaseService:
    """Small wrapper for local SQLite access."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = Path(
            db_path or Path.home() / ".youtube_downloader_history.sqlite"
        )
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
