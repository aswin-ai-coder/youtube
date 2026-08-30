from pathlib import Path

from app.core import download_engine
from app.core.download_engine import DownloadEngine
from app.core.models import DownloadKind, DownloadOptions


def test_download_engine_builds_h264_aac_format(tmp_path):
    options = DownloadOptions(
        url="https://example.com/video",
        output_dir=tmp_path,
        kind=DownloadKind.VIDEO_AUDIO,
        quality="1080p",
        audio_codec="aac",
        video_codec="h264",
    )
    fmt = DownloadEngine().build_format(options)
    assert "height<=1080" in fmt
    assert "vcodec*=avc1" in fmt
    assert "acodec*=mp4a" in fmt


def test_download_engine_builds_audio_format(tmp_path):
    options = DownloadOptions(
        url="https://example.com/video",
        output_dir=tmp_path,
        kind=DownloadKind.AUDIO,
        audio_codec="mp3",
    )
    assert DownloadEngine().build_format(options) == "bestaudio/best"


def test_download_engine_preserves_embedding_options(tmp_path):
    options = DownloadOptions(
        url="https://example.com/video",
        output_dir=tmp_path,
        kind=DownloadKind.AUDIO,
        embed_thumbnail=False,
        embed_metadata=False,
    )
    built = DownloadEngine().build_options(options)
    assert built["postprocessors"][0]["key"] == "FFmpegExtractAudio"
    assert all(pp["key"] not in {"FFmpegMetadata", "EmbedThumbnail"} for pp in built["postprocessors"])


def test_download_returns_finalized_output_path(tmp_path, monkeypatch):
    output = tmp_path / "example.mp3"

    class FakeYoutubeDL:
        last_options = None

        def __init__(self, options):
            FakeYoutubeDL.last_options = options

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def download(self, urls):
            progress = FakeYoutubeDL.last_options["progress_hooks"][0]
            progress({"status": "finished", "filename": str(tmp_path / "example.webm")})
            postprocess = FakeYoutubeDL.last_options["postprocessor_hooks"][0]
            postprocess({"status": "finished", "info_dict": {"filepath": str(output)}})
            return 0

    monkeypatch.setattr(download_engine, "YoutubeDL", FakeYoutubeDL)
    options = DownloadOptions(url="https://example.com/video", output_dir=tmp_path, kind=DownloadKind.AUDIO)
    assert DownloadEngine().download(options) == str(output)
    assert Path(output).parent == tmp_path
