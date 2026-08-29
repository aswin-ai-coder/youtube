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
    options = DownloadOptions(url="https://example.com/video", output_dir=tmp_path, kind=DownloadKind.AUDIO, audio_codec="mp3")
    assert DownloadEngine().build_format(options) == "bestaudio/best"
