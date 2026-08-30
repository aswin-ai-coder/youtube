[app]
title = YouTube Downloader
package.name = youtubedownloader
package.domain = org.local
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,json,txt,md
source.exclude_dirs = youtub,build,dist,.buildozer,__pycache__,.git
version = 1.0.5
requirements = python3,kivy==2.3.1,kivymd==2.0.0,materialyoucolor==3.0.3,materialshapes,exceptiongroup,asyncgui,asynckivy,yt-dlp,requests,pillow,certifi,plyer
orientation = all
fullscreen = 0
android.permissions = INTERNET,POST_NOTIFICATIONS,FOREGROUND_SERVICE
android.api = 35
android.minapi = 23
android.archs = arm64-v8a
p4a.branch = v2024.01.21
services = downloader:service/main.py

# Use the platform launch activity only; the real Kivy UI is rendered
# immediately by app/ui/android/app.py without an in-app Loading screen.

[buildozer]
log_level = 2
warn_on_root = 1
