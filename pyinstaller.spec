# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# collect_all trae binaries, datas e hiddenimports del paquete completo
tklinenums_datas, tklinenums_binaries, tklinenums_hiddenimports = collect_all('tklinenums')
ctk_datas, ctk_binaries, ctk_hiddenimports = collect_all('customtkinter')
ctkmsg_datas, ctkmsg_binaries, ctkmsg_hiddenimports = collect_all('CTkMessagebox')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[
        *tklinenums_binaries,
        *ctk_binaries,
        *ctkmsg_binaries,
    ],
    datas=[
        ('translations', 'translations'),
        ('data', 'data'),
        ('plugins', 'plugins'),
        ('config', 'config'),
        *tklinenums_datas,
        *ctk_datas,
        *ctkmsg_datas,
    ],
    hiddenimports=[
        'customtkinter',
        'CTkMessagebox',
        'PIL',
        'tklinenums',
        *tklinenums_hiddenimports,
        *ctk_hiddenimports,
        *ctkmsg_hiddenimports,
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
    name='CTkDesigner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
# Sin bloque COLLECT — onefile no lo necesita
