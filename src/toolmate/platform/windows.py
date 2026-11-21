import ctypes
import os
from pathlib import Path
from typing import Any


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


def read_user_environment() -> tuple[str | None, str | None]:
    import winreg

    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            "Environment",
            0,
            winreg.KEY_QUERY_VALUE,
        ) as key:
            path = _read_environment_value(key, "Path")
            esim_home = _read_environment_value(key, "ESIM_HOME")
    except FileNotFoundError:
        return None, None
    return path, esim_home


def write_user_environment(path: str | None, esim_home: str | None) -> None:
    import winreg

    with winreg.CreateKeyEx(
        winreg.HKEY_CURRENT_USER,
        "Environment",
        0,
        winreg.KEY_SET_VALUE,
    ) as key:
        if path is not None:
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, path)
        if esim_home is not None:
            winreg.SetValueEx(key, "ESIM_HOME", 0, winreg.REG_SZ, esim_home)


def _read_environment_value(key: Any, name: str) -> str | None:
    import winreg

    try:
        value, _ = winreg.QueryValueEx(key, name)
    except FileNotFoundError:
        return None
    return value if isinstance(value, str) else None
