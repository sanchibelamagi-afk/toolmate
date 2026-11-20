from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True)
class SystemInfo:
    operating_system: str
    os_version: str
    architecture: str
    package_managers: tuple[str, ...]
    administrator: bool
    esim_path: Path | None
    environment_variables: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class DetectedInstallation:
    version: str | None
    path: Path | None
    detection_method: str


@dataclass(frozen=True)
class DependencyInventoryEntry:
    id: str
    name: str
    status: str
    installations: tuple[DetectedInstallation, ...]
    error: str | None = None
