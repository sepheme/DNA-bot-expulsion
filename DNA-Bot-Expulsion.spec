# -*- mode: python ; coding: utf-8 -*-

import PyInstaller.utils.hooks as hooks

block_cipher = None

# Collect win10toast data files
try:
    win10toast_datas = hooks.collect_data_files('win10toast')
    # Ensure it's a list
    if not isinstance(win10toast_datas, list):
        win10toast_datas = list(win10toast_datas) if win10toast_datas else []
except Exception:
    win10toast_datas = []

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets'), ('config.json', '.')] + win10toast_datas,
    hiddenimports=[
        'win10toast',
        'pynput.keyboard',
        'pynput.mouse',
        'pyautogui',
        'pygetwindow',
        'tkinter',
        'win10toast.toast',
        'pydirectinput',
    ],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DNA-Bot-Expulsion',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Enable UPX compression if available
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='NONE',
)

