[app]
title = YouTube Downloader
package.name = youtubedownloader
package.domain = org.local
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,json,txt,md,atlas
source.exclude_dirs = youtub,build,dist,.buildozer,__pycache__,.git,tests,docs
version = 1.0.7
requirements = python3,kivy==2.3.1,kivymd==2.0.0,materialyoucolor==3.0.3,materialshapes,exceptiongroup,asyncgui,asynckivy,yt-dlp==2026.8.19,requests,pillow,certifi,plyer,pyjnius,openssl,ffmpeg,av_codecs
orientation = portrait
fullscreen = 0
icon.filename = app/assets/icons/icon.png
android.permissions = INTERNET,POST_NOTIFICATIONS,FOREGROUND_SERVICE,FOREGROUND_SERVICE_DATA_SYNC,WAKE_LOCK
android.api = 36
android.minapi = 23
android.ndk = 28c
android.archs = arm64-v8a
services = downloader:service/main.py:foreground:sticky:foregroundServiceType=dataSync

[buildozer]
log_level = 2
warn_on_root = 1
