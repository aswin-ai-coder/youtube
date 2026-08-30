# YouTube Downloader

A cross-platform YouTube media downloader with a shared Python/yt-dlp core, a PySide6 desktop UI, and a Kivy/KivyMD Android UI.

## Current architecture

- `app/core/` — shared models, yt-dlp engine, queue, history, settings, playlists, favorites, subtitles, thumbnails, notifications, and update checks.
- `app/ui/desktop/` — PySide6 desktop application.
- `app/ui/android/` — Kivy/KivyMD Android application.
- `service/main.py` — Android background queue worker. Android uses this as the single download worker so the UI and background service do not race over the same queue.

## Desktop development

```bash
cd ~/Projects/youtube
source youtub/bin/activate
pip install -r requirements.txt
python -m app.main
```

Use the package-module form above rather than `python app/main.py`, because the application uses the `app.*` package namespace.

## Android build

```bash
buildozer android debug
```

The Android build uses `app/mobile_main.py` and the background service configured in `buildozer.spec`.

## Tests

```bash
python -m pytest -q
python -m compileall -q app main.py service
```

## CI

GitHub Actions validates Python tests and compilation, Android UI imports and screen construction, the desktop executable build, and the Android debug APK build.

## Notes

- FFmpeg is required for merging, audio extraction/conversion, and media post-processing.
- yt-dlp changes frequently; keeping it updated is important for extractor compatibility.
- Android background downloads depend on the platform service lifecycle and available storage/FFmpeg support.
