# YouTube Downloader

A cross-platform YouTube video and music downloader built around a shared Python
backend, PySide6 desktop UI, yt-dlp, FFmpeg, and SQLite.

## Features

- Analyze YouTube videos, playlists, channels, and shorts
- Download video, audio, or merged video + audio
- Prefer H264/AVC video and AAC audio with automatic yt-dlp fallback
- Select available video qualities, audio codecs, bitrates, and containers
- Download subtitles and optionally embed them
- Persist download history in SQLite
- Save settings locally as JSON, including theme, retries, FFmpeg path, and layout
- Queue downloads with progress/status tracking
- Cache and display large thumbnails
- Dark/light desktop themes with configurable accent color

## Run

```bash
cd ~/Projects/youtube
source youtub/bin/activate
python app/main.py
```

## Tests

```bash
cd ~/Projects/youtube
source youtub/bin/activate
pytest -q tests/test_core_services.py
```

## Build

See [docs/build.md](docs/build.md) for PyInstaller, AppImage, and deb packaging.

## Android

See [docs/android.md](docs/android.md). The Android UI should reuse the services in
`app/core` and keep platform-specific code in mobile UI modules only.
