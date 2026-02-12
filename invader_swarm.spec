# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['invader_swarm.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/images/background/*.png', 'assets/images/backgrounds'),
        ('assets/images/bosses/*.png', 'assets/images/bosses'),
        ('assets/images/enemies/*.png', 'assets/images/enemies'),
        ('assets/images/player/*.png', 'assets/images/player'),
        ('assets/images/powerups/*.png', 'assets/images/powerups'),
        ('assets/sounds/*.mp3', 'assets/sounds'),
        ('high_scores.json', '.')
    ],
    hiddenimports=[],
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
    name='invader_swarm',
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
    icon='game.ico'  # Add this if you have an icon
)