import os
from pathlib import Path


def is_administrator() -> bool:
    return os.geteuid() == 0


def common_esim_paths() -> list[Path]:
    home = Path(os.environ.get("HOME", str(Path.home())))
    return [
        home / "eSim",
        home / "esim",
        Path("/Applications/eSim"),
        Path("/opt/eSim"),
    ]


def user_profile_path() -> Path:
    return Path.home() / ".zprofile"
