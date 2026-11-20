import ctypes
import os
from pathlib import Path


def is_administrator() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except (AttributeError, OSError):
        return False


def common_esim_paths() -> list[Path]:
    program_files = os.environ.get("ProgramFiles")
    local_app_data = os.environ.get("LOCALAPPDATA")
    paths = []
    if program_files:
        paths.append(Path(program_files) / "eSim")
    if local_app_data:
        paths.append(Path(local_app_data) / "eSim")
    return paths
