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
