import sqlite3
from pathlib import Path
from typing import Any


class HistoryService:
    """SQLite-backed history store for completed and failed downloads."""

    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path or Path.home() / ".youtube_downloader_history.sqlite")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    date TEXT NOT NULL,
                    duration INTEGER,
                    size_bytes INTEGER,
                    output_path TEXT,
                    thumbnail_url TEXT,
                    status TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def add_record(
        self,
        *,
        title: str,
        url: str,
        duration: int | None = None,
        size_bytes: int | None = None,
        output_path: str | None = None,
        thumbnail_url: str | None = None,
        status: str = "completed",
    ) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO history (title, url, date, duration, size_bytes, output_path, thumbnail_url, status)
                VALUES (?, ?, datetime('now'), ?, ?, ?, ?, ?)
                """,
                (title, url, duration, size_bytes, output_path, thumbnail_url, status),
            )
            conn.commit()

    def list_recent(self, limit: int = 20) -> list[dict[str, Any]]:
        return self.search(limit=limit)

    def search(
        self,
        *,
        query: str = "",
        status: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        where: list[str] = []
        params: list[Any] = []
        if query:
            where.append("(title LIKE ? OR url LIKE ? OR output_path LIKE ?)")
            pattern = f"%{query}%"
            params.extend([pattern, pattern, pattern])
        if status:
            where.append("status = ?")
            params.append(status)
        clause = f"WHERE {' AND '.join(where)}" if where else ""
        params.append(limit)
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                f"""
                SELECT id, title, url, date, duration, size_bytes, output_path, thumbnail_url, status
                FROM history
                {clause}
                ORDER BY id DESC
                LIMIT ?
                """,
                params,
            ).fetchall()

        return [
            {
                "id": row_id,
                "title": title,
                "url": url,
                "date": date,
                "duration": duration,
                "size_bytes": size_bytes,
                "output_path": output_path,
                "thumbnail_url": thumbnail_url,
                "status": status,
            }
            for (
                row_id,
                title,
                url,
                date,
                duration,
                size_bytes,
                output_path,
                thumbnail_url,
                status,
            ) in rows
        ]

    def delete(self, record_id: int) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM history WHERE id = ?", (record_id,))
            conn.commit()

    def get(self, record_id: int) -> dict[str, Any] | None:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT id, title, url, date, duration, size_bytes, output_path, thumbnail_url, status
                FROM history
                WHERE id = ?
                """,
                (record_id,),
            ).fetchone()
        if row is None:
            return None
        keys = [
            "id",
            "title",
            "url",
            "date",
            "duration",
            "size_bytes",
            "output_path",
            "thumbnail_url",
            "status",
        ]
        return dict(zip(keys, row, strict=True))

    def clear(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM history")
            conn.commit()
