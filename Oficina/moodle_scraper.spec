# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec para moodle_scraper.py
# Inclui o driver do Playwright (node.exe + package/) no bundle.

import sys
from pathlib import Path
import playwright as _pw

_driver = Path(_pw.__file__).parent / "driver"

a = Analysis(
    ["moodle_scraper.py"],
    pathex=[],
    binaries=[],
    datas=[(str(_driver), "playwright/driver")],
    hiddenimports=[
        "playwright",
        "playwright.sync_api",
        "pyee",
        "pyee.asyncio",
        "pyee.base",
        "greenlet",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "numpy", "pandas"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="moodle_scraper",
    debug=False,
    strip=False,
    upx=False,
    console=True,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="moodle_scraper",
)
