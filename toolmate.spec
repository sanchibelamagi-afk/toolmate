from pathlib import Path

from PyInstaller.utils.hooks import collect_all


project_root = Path(SPECPATH)
textual_datas, textual_binaries, textual_hiddenimports = collect_all("textual")
rich_datas, rich_binaries, rich_hiddenimports = collect_all("rich")

a = Analysis(
    [str(project_root / "main.py")],
    pathex=[str(project_root / "src")],
    binaries=textual_binaries + rich_binaries,
    datas=[
        (str(project_root / "config" / "manifest.yaml"), "config"),
        *textual_datas,
        *rich_datas,
    ],
    hiddenimports=textual_hiddenimports + rich_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="toolmate",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
)
