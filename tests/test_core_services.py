from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from core.history_service import HistoryService
from core.download_service import DownloadService
from core.models import DownloadKind, DownloadOptions
from core.queue_service import QueueItem, QueueService
from core.settings_service import SettingsService


def test_history_round_trip(tmp_path):
    db_path = tmp_path / "history.sqlite"
    history = HistoryService(db_path)

    history.add_record(
        title="Demo video",
        url="https://example.com/video",
        duration=120,
        size_bytes=2048,
        output_path=str(tmp_path / "demo.mp4"),
        thumbnail_url="https://example.com/thumb.jpg",
        status="completed",
    )

    records = history.list_recent(limit=5)
    assert len(records) == 1
    assert records[0]["title"] == "Demo video"


def test_settings_persistence(tmp_path):
    settings_path = tmp_path / "settings.json"
    settings = SettingsService(settings_path)
    settings.set("theme", "dark")
    settings.set("download_folder", str(tmp_path / "downloads"))
    settings.save()

    reloaded = SettingsService(settings_path)
    assert reloaded.get("theme") == "dark"
    assert reloaded.get("download_folder") == str(tmp_path / "downloads")


def test_settings_defaults_are_present(tmp_path):
    settings = SettingsService(tmp_path / "settings.json")

    assert settings.get("filename_template") == "%(title)s.%(ext)s"
    assert settings.get("max_retries") == 10


def test_history_search_and_delete(tmp_path):
    history = HistoryService(tmp_path / "history.sqlite")
    history.add_record(title="Alpha", url="https://example.com/a", status="completed")
    history.add_record(title="Beta", url="https://example.com/b", status="failed")

    rows = history.search(query="Alpha")
    assert len(rows) == 1
    assert rows[0]["title"] == "Alpha"

    history.delete(rows[0]["id"])
    assert history.search(query="Alpha") == []


def test_queue_updates_and_reorders(tmp_path):
    queue = QueueService()
    first = queue.enqueue(QueueItem(url="a", output_dir=str(tmp_path)))
    second = queue.enqueue(QueueItem(url="b", output_dir=str(tmp_path)))

    assert queue.move(second.id, -1)
    assert queue.list_items()[0].id == second.id

    queue.update(first.id, progress=55)
    assert queue.get(first.id).progress == 55


def test_download_options_prefer_h264_and_aac(tmp_path):
    service = DownloadService()
    options = DownloadOptions(
        url="https://example.com",
        output_dir=tmp_path,
        kind=DownloadKind.VIDEO_AUDIO,
        quality="1080p",
        audio_codec="aac",
    )

    fmt = service.build_format(options)
    assert "height<=1080" in fmt
    assert "vcodec*=avc1" in fmt
    assert "acodec*=mp4a" in fmt
