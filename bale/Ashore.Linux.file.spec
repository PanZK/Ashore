# -*- mode: python ; coding: utf-8 -*-


block_cipher = None
#['cryptography','lib-dynload','numpy','libcrypto','libcrypto.1.1','QtDBus','libncursesw','libncursesw.5','libssl','libssl.1.1','QtSvg']

a = Analysis(['../Ashore.py'],
             pathex=[],
             binaries=[],
             datas=[('../static','static'),('../config','config')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=['cryptography','lib-dynload','numpy','libcrypto','libcrypto.1.1','QtDBus','libncursesw','libncursesw.5','libssl','libssl.1.1','QtSvg'],
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
          name='Ashore',
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
          entitlements_file=None ,)
app = BUNDLE(exe,
             name='Ashore.app',
             bundle_identifier=None)
