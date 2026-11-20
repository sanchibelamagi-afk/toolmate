import os
import platform
import sys
from pathlib import Path

from toolmate.core.models import SystemInfo
from toolmate.detection.package_manager_detector import detect_package_managers
from toolmate.platform import linux, windows
from toolmate.platform.paths import first_existing_path


ESIM_ENVIRONMENT_VARIABLES = (
    "ESIM",
    "ESIM_HOME",
    "ESIM_PATH",
    "PYTHONPATH",
)


def locate_esim() -> Path | None:
    for variable in ESIM_ENVIRONMENT_VARIABLES:
        value = os.environ.get(variable)
        if not value:
            continue
        candidate = Path(value)
        if candidate.exists():
            return candidate.resolve()

    if sys.platform.startswith("win"):
        candidates = windows.common_esim_paths()
    else:
        candidates = linux.common_esim_paths()
    return first_existing_path(candidates)


def detect_system_info() -> SystemInfo:
    if sys.platform.startswith("win"):
        operating_system = "Windows"
        administrator = windows.is_administrator()
    else:
        operating_system = "Linux"
        administrator = linux.is_administrator()

    environment = {
        name: os.environ[name]
        for name in ESIM_ENVIRONMENT_VARIABLES
        if os.environ.get(name)
    }

    return SystemInfo(
        operating_system=operating_system,
        os_version=platform.platform(),
        architecture=platform.machine() or "Unknown",
        package_managers=detect_package_managers(),
        administrator=administrator,
        esim_path=locate_esim(),
        environment_variables=environment,
    )
