# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['video_downloader_gui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets', 'PyQt6.QtWebEngine', 'PyQt6.QtWebEngineWidgets'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Add qt-material resources
import os
import qt_material
material_path = os.path.dirname(qt_material.__file__)
a.datas += [(os.path.join('qt_material', file), os.path.join(material_path, file), 'DATA') 
            for file in os.listdir(material_path) if file.endswith('.xml')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VideoDownloader',
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
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)

if platform.system() == 'Darwin':
    app = BUNDLE(
        exe,
        name='VideoDownloader.app',
        icon='icon.icns' if os.path.exists('icon.icns') else None,
        bundle_identifier='com.tolstoyj.videodownloader',
        info_plist={
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleVersion': '1.0.0',
            'NSHighResolutionCapable': True,
            'LSMinimumSystemVersion': '10.15',
        },
    )
