# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ["entrypoint.py"],
    pathex=[
        "./env/Lib/site-packages",
        "./app"
    ],
    binaries=[],
    datas=[
        (
            "./.env",
            ".",
        ),
        (
            "./app/config_files",
            "app/config_files",
        ),
        (
            "./app/logs",
            "app/logs",
        )
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    options=[("X utf8", None, "OPTION")],
    exclude_binaries=True,
    name="localmusicmanager",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="entrypoint",
)
