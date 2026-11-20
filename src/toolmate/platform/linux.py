import os
from pathlib import Path


def is_administrator() -> bool:
    return os.geteuid() == 0


def common_esim_paths() -> list[Path]:
    home = Path(os.environ.get("HOME", str(Path.home())))
    return [
        home / "eSim",
        home / "esim",
        Path("/opt/eSim"),
        Path("/usr/local/eSim"),
    ]
