import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Iterable

from toolmate.core.models import DetectedInstallation


VERSION_PATTERN = re.compile(r"(\d+(?:\.\d+)+(?:[-+._]?[A-Za-z0-9.-]+)?)")


def _expand_path(value: str) -> Path:
    return Path(os.path.expandvars(value))


def detect_executables(
    executable: str,
    version_args: Iterable[str] = (),
    known_paths: Iterable[str] = (),
) -> list[DetectedInstallation]:
    found: dict[Path, DetectedInstallation] = {}

    executable_path = shutil.which(executable)
    if executable_path:
        path = Path(executable_path).resolve()
        found[path] = DetectedInstallation(
            version=_get_version(path, version_args),
            path=path,
            detection_method="executable",
        )

    for known_path in known_paths:
        candidate = _expand_path(known_path)
        if candidate.is_dir():
            nested = _find_executable_in_directory(candidate, executable)
            for path in nested:
                found[path] = DetectedInstallation(
                    version=_get_version(path, version_args),
                    path=path,
                    detection_method="known_path",
                )
        elif candidate.is_file():
            found[candidate.resolve()] = DetectedInstallation(
                version=_get_version(candidate, version_args),
                path=candidate.resolve(),
                detection_method="known_path",
            )

    return list(found.values())


def _find_executable_in_directory(directory: Path, executable: str) -> list[Path]:
    matches: list[Path] = []
    names = {executable, f"{executable}.exe", f"{executable}.cmd"}
    try:
        for path in directory.rglob("*"):
            if path.is_file() and path.name.lower() in {name.lower() for name in names}:
                matches.append(path.resolve())
    except OSError:
        return matches
    return matches


def _get_version(executable: Path, version_args: Iterable[str]) -> str | None:
    try:
        result = subprocess.run(
            [str(executable), *version_args],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None

    output = "\n".join((result.stdout, result.stderr)).strip()
    if not output:
        return None
    match = VERSION_PATTERN.search(output)
    return match.group(1) if match else None
