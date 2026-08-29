from __future__ import annotations

import sqlite3
from pathlib import Path


class SearchHistoryService:

    def __init__(self):

        folder = Path.home() / ".youtube_downloader"
        folder.mkdir(exist_ok=True)

        self.db = sqlite3.connect(folder / "history.db")

        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS searches(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT,
                title TEXT,
                searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        self.db.commit()

    def add(self, url: str, title: str):

        self.db.execute(
            "INSERT INTO searches(url,title) VALUES(?,?)",
            (url, title),
        )

        self.db.commit()

    def latest(self, limit=50):

        cursor = self.db.execute(
            """
            SELECT url,title,searched_at
            FROM searches
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )

        return cursor.fetchall()

    def clear(self):

        self.db.execute(
            "DELETE FROM searches"
        )

        self.db.commit()
