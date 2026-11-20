import sys
from pathlib import Path

from toolmate.core.models import DetectedInstallation


def detect_installed_registry_entry(
    display_name: str,
    roots: tuple[int, ...] = (),
) -> list[DetectedInstallation]:
    if not sys.platform.startswith("win"):
        return []

    try:
        import winreg
    except ImportError:
        return []

    selected_roots = roots or (
        winreg.HKEY_LOCAL_MACHINE,
        winreg.HKEY_CURRENT_USER,
    )
    registry_paths = (
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
    )
    detections: dict[Path | str, DetectedInstallation] = {}

    for root in selected_roots:
        for registry_path in registry_paths:
            try:
                with winreg.OpenKey(root, registry_path) as key:
                    index = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(key, index)
                            index += 1
                        except OSError:
                            break

                        try:
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                values = {
                                    "DisplayName": winreg.QueryValueEx(subkey, "DisplayName")[0],
                                }
                                try:
                                    values["DisplayVersion"] = winreg.QueryValueEx(
                                        subkey, "DisplayVersion"
                                    )[0]
                                except OSError:
                                    values["DisplayVersion"] = None
                                try:
                                    values["InstallLocation"] = winreg.QueryValueEx(
                                        subkey, "InstallLocation"
                                    )[0]
                                except OSError:
                                    values["InstallLocation"] = None
                        except (OSError, KeyError):
                            continue

                        if str(values["DisplayName"]).lower() != display_name.lower():
                            continue

                        location = values["InstallLocation"]
                        path = Path(location).resolve() if location else None
                        key_name = str(path or subkey_name)
                        detections[key_name] = DetectedInstallation(
                            version=values["DisplayVersion"],
                            path=path,
                            detection_method="windows_registry",
                        )
            except OSError:
                continue

    return list(detections.values())
