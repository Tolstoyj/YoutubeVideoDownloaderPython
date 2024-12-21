#!/usr/bin/env python3

import os
import sys
import platform
import subprocess
from pathlib import Path

def create_spec_file():
    """Create a PyInstaller spec file with custom settings."""
    return '''# -*- mode: python ; coding: utf-8 -*-

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
'''

def build_executable():
    """Build the executable for the current platform."""
    # Create spec file
    spec_content = create_spec_file()
    with open('VideoDownloader.spec', 'w') as f:
        f.write(spec_content)
    
    # Create dist and build directories
    os.makedirs('dist', exist_ok=True)
    os.makedirs('build', exist_ok=True)
    
    # Build the executable
    subprocess.run(['pyinstaller', '--clean', 'VideoDownloader.spec'])
    
    # Create release directory
    release_dir = Path('release')
    release_dir.mkdir(exist_ok=True)
    
    # Package the release
    if platform.system() == 'Windows':
        # Copy the executable and create a ZIP file
        import shutil
        import zipfile
        
        exe_path = Path('dist/VideoDownloader.exe')
        if exe_path.exists():
            release_zip = release_dir / 'VideoDownloader-Windows.zip'
            with zipfile.ZipFile(release_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(exe_path, exe_path.name)
                zipf.write('README.md')
                zipf.write('LICENSE')
            print(f"Windows release created: {release_zip}")
    
    elif platform.system() == 'Darwin':
        # Create a DMG file
        app_path = Path('dist/VideoDownloader.app')
        if app_path.exists():
            dmg_path = release_dir / 'VideoDownloader-macOS.dmg'
            subprocess.run([
                'hdiutil', 'create', '-volname', 'VideoDownloader',
                '-srcfolder', app_path, '-ov', '-format', 'UDZO',
                dmg_path
            ])
            print(f"macOS release created: {dmg_path}")

if __name__ == '__main__':
    build_executable() 