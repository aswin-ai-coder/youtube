# Android Build

The Android frontend is `app/ui/android` and uses the same yt-dlp/download engine as desktop without importing PySide6.

## Prerequisites

```bash
cd ~/Projects/youtube
source youtub/bin/activate
pip install -r requirements.txt
```

Install Android SDK/NDK and Buildozer according to the Buildozer documentation for your Linux distribution.

## Build a debug APK

```bash
buildozer android clean
buildozer android debug
```

Install the generated APK on a connected device with your preferred Android tooling.

## Run from the project root

`main.py` is the Android/Kivy entrypoint. The desktop application remains available through:

```bash
python -m app.main
```

## Architecture

- `app/ui/android/app.py` — KivyMD application shell.
- `app/ui/android/screens/home_screen.py` — analysis and download UI.
- `app/core/android_download_coordinator.py` — Kivy-safe background download coordination.
- `app/core/download_engine.py` — UI-independent yt-dlp engine shared with desktop.
- `app/core/queue_service.py` — persistent queue with recovery and thread-safe writes.

## FFmpeg

Video-only downloads that require no post-processing can work with yt-dlp alone. Audio conversion, subtitle embedding, metadata processing, and thumbnail embedding require an FFmpeg binary available to the target platform. Android packaging therefore needs an Android-compatible FFmpeg integration before those post-processing features can be considered release-ready.

## Validation

Before packaging:

```bash
python -m compileall app
python -m pytest -q
```

The Android UI should be tested on a real device because Android storage, notifications, background execution, and FFmpeg behavior cannot be fully validated by desktop Python tests.
