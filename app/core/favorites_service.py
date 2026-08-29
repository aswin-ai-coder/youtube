from __future__ import annotations

import sqlite3
from pathlib import Path


class FavoritesService:

    def __init__(self):

        folder = Path.home() / ".youtube_downloader"
        folder.mkdir(exist_ok=True)

        self.db = sqlite3.connect(folder / "favorites.db")

        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS favorites(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                title TEXT,
                thumbnail TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        self.db.commit()

    def add(self, url, title, thumbnail=""):

        self.db.execute(
            """
            INSERT OR IGNORE INTO favorites
            (url,title,thumbnail)
            VALUES(?,?,?)
            """,
            (url, title, thumbnail),
        )

        self.db.commit()

    def remove(self, url):

        self.db.execute(
            "DELETE FROM favorites WHERE url=?",
            (url,),
        )

        self.db.commit()

    def all(self):

        cursor = self.db.execute(
            """
            SELECT
                url,
                title,
                thumbnail
            FROM favorites
            ORDER BY id DESC
            """
        )

        return cursor.fetchall()
