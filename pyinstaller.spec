# -*- mode: python -*-
import os
block_cipher = None

# Tesseract OCR paths - adjust these if your Tesseract installation is in a different location
# IMPORTANT: Tesseract must be installed on the build machine for this to work
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
TESSERACT_DIR = r'C:\Program Files\Tesseract-OCR'
TESSERACT_EXE = os.path.join(TESSERACT_DIR, 'tesseract.exe')
TESSERACT_TESSDATA = os.path.join(TESSERACT_DIR, 'tessdata')

# Build list of Tesseract binaries to include
tesseract_binaries = []
if os.path.exists(TESSERACT_DIR):
    # Include main executable
    if os.path.exists(TESSERACT_EXE):
        tesseract_binaries.append((TESSERACT_EXE, 'Tesseract-OCR'))
    # Include DLL files from Tesseract directory
    try:
        for file in os.listdir(TESSERACT_DIR):
            if file.endswith('.dll'):
                dll_path = os.path.join(TESSERACT_DIR, file)
                tesseract_binaries.append((dll_path, 'Tesseract-OCR'))
    except Exception as e:
        print(f"Warning: Could not scan Tesseract directory for DLLs: {e}")

# Build list of Tesseract data files
tesseract_datas = []
if os.path.exists(TESSERACT_TESSDATA):
    tesseract_datas.append((TESSERACT_TESSDATA, 'Tesseract-OCR/tessdata'))
else:
    print(f"Warning: Tesseract tessdata directory not found at {TESSERACT_TESSDATA}")
    print("The executable will still work if Tesseract is installed on the target system.")

a = Analysis(['main.py'],
             pathex=['.'],
             binaries=tesseract_binaries,
             datas=[('assets/img', 'assets/img')] + tesseract_datas,
             hiddenimports=[
                 'pyautogui',
                 'pygetwindow',
                 'pynput',
                 'pynput.keyboard',
                 'pytesseract',
                 'PIL',
                 'PIL.Image',
                 'PIL.ImageGrab',
                 'PIL.ImageFilter',
                 'numpy',
                 'cv2',  # opencv-python
                 'tkinter',
                 'tkinter.messagebox',
             ],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
           cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='DNA-bot-expulsion',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True,
          disable_windowed_traceback=False,
          argv_emulation=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          icon=None)