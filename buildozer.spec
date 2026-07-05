[app]
title = YouTube Downloader
package.name = youtubedownloader
package.domain = org.local
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,json,txt,md
source.exclude_dirs = youtub,build,dist,.buildozer,__pycache__
version = 1.0.0
requirements = python3,kivy,yt-dlp,requests,pillow,certifi
orientation = all
fullscreen = 0
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,POST_NOTIFICATIONS
android.api = 35
android.minapi = 23
android.entrypoint = org.renpy.android.PythonActivity
android.archs = arm64-v8a
p4a.branch = v2024.01.21
p4a.url = file:///home/user/hostcwd/.buildozer/android/platform/python-for-android-local
[buildozer]
log_level = 2
warn_on_root = 1
