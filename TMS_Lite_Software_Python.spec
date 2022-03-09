# -*- mode: python ; coding: utf-8 -*-

import os

spec_root = os.path.abspath(SPECPATH)

block_cipher = None

def include_dir(mydir):
    def rec_glob(p, files):
        import glob
        for d in glob.glob(p):
            if os.path.isfile(d):
                files.append(d)
            rec_glob("%s/*" % d, files)
    files = []
    rec_glob("%s/*" % mydir, files)
    extra_data = []
    for f in files:
        extra_data.append((f, f, 'DATA'))

    return extra_data

folder_list = ['Tk_MsgBox', 'TMS Icon', 'TMS_Web_Resources', 'report src', 'Font', 'TMS_Saved_Images'
, 'TMS_Saved_Reports', 'tessdata', 'DEPENDENCIES', 'LC-18 Picture GUI', 'mpl-data'
, 'MVS-Python']

def include_file(file_path):
  import re
  file_data = []
  if os.path.isfile(file_path):
    file_name = str((re.findall(r'[^\\/]+|[\\/]', file_path))[-1])
    file_data.append((file_name, file_path, 'DATA'))

  return file_data


file_list = [spec_root + '\\LC20Library.dll', spec_root + '\\LC18Library.dll', spec_root + '\\UsbLibrary.dll', spec_root + '\\VirtualFG40.dll']

a = Analysis(['TMS_Lite_Software_Python.py'],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['shiboken2', 'PySide2', 'skimage', 'scipy'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

for folder_data in folder_list:
  a.datas += include_dir(folder_data)

for file_data in file_list:
  a.datas += include_file(file_data)
  
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='TMS-Lite Software',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          icon= spec_root+'\\TMS Icon\\logo4.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='TMS-Lite-Software-General')
