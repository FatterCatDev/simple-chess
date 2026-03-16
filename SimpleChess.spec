# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_submodules

# __file__ is not guaranteed when PyInstaller evaluates a spec in CI.
project_root = os.path.abspath(globals().get("SPECPATH", os.getcwd()))
src_dir = os.path.join(project_root, "src")

datas = [
    (os.path.join(src_dir, "gui", "assets"), "gui/assets"),
    (os.path.join(src_dir, "ai", "stockfish", "shared"), "ai/stockfish/shared"),
]

if sys.platform.startswith("win"):
    binaries = [
        (
            os.path.join(src_dir, "ai", "stockfish", "windows", "avx2", "stockfish-windows-x86-64-avx2.exe"),
            "ai/stockfish/windows/avx2",
        ),
        (
            os.path.join(src_dir, "ai", "stockfish", "windows", "non-avx2", "stockfish-windows-x86-64.exe"),
            "ai/stockfish/windows/non-avx2",
        ),
    ]
elif sys.platform.startswith("darwin"):
    binaries = [
        (
            os.path.join(src_dir, "ai", "stockfish", "macos", "avx2", "stockfish-macos-x86-64-avx2"),
            "ai/stockfish/macos/avx2",
        ),
        (
            os.path.join(src_dir, "ai", "stockfish", "macos", "non-avx2", "stockfish-macos-x86-64"),
            "ai/stockfish/macos/non-avx2",
        ),
    ]
else:
    binaries = [
        (
            os.path.join(src_dir, "ai", "stockfish", "ubuntu", "avx2", "stockfish-ubuntu-x86-64-avx2"),
            "ai/stockfish/ubuntu/avx2",
        ),
        (
            os.path.join(src_dir, "ai", "stockfish", "ubuntu", "non-avx2", "stockfish-ubuntu-x86-64"),
            "ai/stockfish/ubuntu/non-avx2",
        ),
    ]

hiddenimports = collect_submodules("PIL")

a = Analysis(
    ["src/main.py"],
    pathex=[src_dir],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="SimpleChess",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
