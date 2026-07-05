# Android Build Plan

This project includes a working Android packaging manifest at `buildozer.spec`.
The mobile UI lives in `app/ui/mobile`, and shared backend services live in
`app/core`.

## Run on Android device or emulator

1. Activate the project environment:

```bash
cd ~/Projects/youtube
source youtub/bin/activate
```

2. Install Python requirements and Buildozer:

```bash
pip install -r requirements.txt
pip install buildozer
```

3. Build and install a debug APK:

```bash
buildozer android debug deploy run
```

4. If you need only the APK without installing:

```bash
buildozer android debug
```

5. Produce a release APK once testing is complete:

```bash
buildozer android release
buildozer android apk
```

6. The generated APK is located in:

```bash
.buildozer/android/platform/build/dists/youtubedownloader/bin/
```

## Entry point and packaging

The Android entrypoint is `app/mobile_main.py`, which starts `YouTubeDownloaderMobileApp`.
The Buildozer manifest includes the application source and excludes the local
Python virtualenv and build artifacts.

Ensure `buildozer.spec` contains:

- `android.entrypoint = app/mobile_main.py`
- `source.dir = .`
- `source.include_exts = py,png,jpg,jpeg,kv,json,txt,md`
- `source.exclude_dirs = youtub,build,dist,.buildozer,__pycache__`

## Permissions

This app requires:

- `INTERNET`
- `READ_EXTERNAL_STORAGE`
- `WRITE_EXTERNAL_STORAGE`
- `POST_NOTIFICATIONS`

## Notes

- The mobile UI shares download logic with the desktop app using `app/core/DownloadService`.
- `SettingsService` stores Android download folder configuration and can be updated from
  `app/ui/mobile/settings.py`.
- FFmpeg must be available on the device or via a compatible Android binary if the app
  downloads formats that require FFmpeg post-processing.

## Validation

Before building Android, validate the shared backend on desktop:

```bash
python -m compileall app
python -m pytest -q tests/test_core_services.py
```

If Android build fails, run:

```bash
buildozer android clean
buildozer android debug deploy run
```
