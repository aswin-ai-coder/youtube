# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ["app/main.py"],
    pathex=["app"],
    binaries=[],
    datas=[("app/assets", "assets")] if __import__("pathlib").Path("app/assets").exists() else [],
    hiddenimports=["yt_dlp", "requests", "PIL"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="youtube-downloader",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="youtube-downloader",
)
