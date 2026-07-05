# Desktop Build

All Python commands must run inside the existing virtual environment.

```bash
cd ~/Projects/youtube
source youtub/bin/activate
pip install -r requirements.txt
```

## PyInstaller

```bash
pyinstaller --clean youtube_downloader.spec
./dist/youtube-downloader/youtube-downloader
```

## AppImage

Build the PyInstaller bundle first, then package it with `appimagetool`.

```bash
mkdir -p packaging/AppDir/usr/bin
cp -r dist/youtube-downloader/* packaging/AppDir/usr/bin/
cat > packaging/AppDir/AppRun <<'EOF'
#!/bin/sh
HERE="$(dirname "$(readlink -f "$0")")"
exec "$HERE/usr/bin/youtube-downloader" "$@"
EOF
chmod +x packaging/AppDir/AppRun
appimagetool packaging/AppDir YouTube-Downloader.AppImage
```

## Debian Package

```bash
mkdir -p packaging/deb/DEBIAN packaging/deb/opt/youtube-downloader packaging/deb/usr/bin
cp -r dist/youtube-downloader/* packaging/deb/opt/youtube-downloader/
cat > packaging/deb/DEBIAN/control <<'EOF'
Package: youtube-downloader
Version: 1.0.0
Section: utils
Priority: optional
Architecture: amd64
Maintainer: Local Build <local@example.com>
Depends: ffmpeg
Description: Cross-platform YouTube video and music downloader
EOF
cat > packaging/deb/usr/bin/youtube-downloader <<'EOF'
#!/bin/sh
exec /opt/youtube-downloader/youtube-downloader "$@"
EOF
chmod +x packaging/deb/usr/bin/youtube-downloader
dpkg-deb --build packaging/deb youtube-downloader_1.0.0_amd64.deb
```

### Build script

Create a simple packaging helper if you want reproducible artifacts:

```bash
#!/bin/sh
set -e
cd "$(dirname "$0")/.."
source youtub/bin/activate
pyinstaller --clean youtube_downloader.spec
mkdir -p packaging/AppDir/usr/bin
cp -r dist/youtube-downloader/* packaging/AppDir/usr/bin/
cat > packaging/AppDir/AppRun <<'EOF'
#!/bin/sh
HERE="$(dirname "$(readlink -f "$0")")"
exec "$HERE/usr/bin/youtube-downloader" "$@"
EOF
chmod +x packaging/AppDir/AppRun
./tools/appimagetool-x86_64.AppImage packaging/AppDir YouTube-Downloader.AppImage
mkdir -p packaging/deb/DEBIAN packaging/deb/opt/youtube-downloader packaging/deb/usr/bin
cp -r dist/youtube-downloader/* packaging/deb/opt/youtube-downloader/
cat > packaging/deb/DEBIAN/control <<'EOF'
Package: youtube-downloader
Version: 1.0.0
Section: utils
Priority: optional
Architecture: amd64
Maintainer: Local Build <local@example.com>
Depends: ffmpeg
Description: Cross-platform YouTube video and music downloader
EOF
cat > packaging/deb/usr/bin/youtube-downloader <<'EOF'
#!/bin/sh
exec /opt/youtube-downloader/youtube-downloader "$@"
EOF
chmod +x packaging/deb/usr/bin/youtube-downloader
dpkg-deb --build packaging/deb youtube-downloader_1.0.0_amd64.deb
```
