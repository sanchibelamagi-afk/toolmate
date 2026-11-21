from __future__ import annotations

import sys
from typing import Any, Iterable, Mapping

from toolmate.core.models import DependencyInventoryEntry, DetectedInstallation
from toolmate.detection.executable_detector import detect_executables, detect_paths
from toolmate.detection.package_manager_detector import (
    detect_package_managers,
    query_package_version,
)
from toolmate.detection.python_package_detector import detect_python_package
from toolmate.detection.registry_detector import detect_installed_registry_entry


class DependencyScanner:
    def __init__(self, manifest: Mapping[str, Any]) -> None:
        dependencies = manifest.get("dependencies")
        if not isinstance(dependencies, list):
            raise ValueError("Manifest dependencies must be a list")
        self.dependencies = dependencies

    def scan(self) -> list[DependencyInventoryEntry]:
        return [self._scan_dependency(dependency) for dependency in self.dependencies]

    def _scan_dependency(self, dependency: Mapping[str, Any]) -> DependencyInventoryEntry:
        dependency_id = str(dependency.get("id", "unknown"))
        name = str(dependency.get("name", dependency_id))
        platforms = dependency.get("platforms")
        if isinstance(platforms, Mapping):
            platform_name = "windows" if sys.platform.startswith("win") else "linux"
            platform = platforms.get(platform_name)
            if isinstance(platform, Mapping) and platform.get("supported") is False:
                return DependencyInventoryEntry(
                    id=dependency_id,
                    name=name,
                    status="unsupported",
                    installations=(),
                )

        try:
            installations = self._detect_installations(dependency)
        except Exception as exc:
            return DependencyInventoryEntry(
                id=dependency_id,
                name=name,
                status="error",
                installations=(),
                error=str(exc),
            )

        if not installations:
            return DependencyInventoryEntry(
                id=dependency_id,
                name=name,
                status="missing",
                installations=(),
            )

        unique = self._deduplicate_installations(installations)
        if unique and all(installation.version is None for installation in unique):
            status = (
                "installed"
                if all(
                    installation.detection_method == "path"
                    for installation in unique
                )
                else "unknown"
            )
        else:
            status = "installed"

        return DependencyInventoryEntry(
            id=dependency_id,
            name=name,
            status=status,
            installations=tuple(unique),
        )

    def _detect_installations(
        self,
        dependency: Mapping[str, Any],
    ) -> list[DetectedInstallation]:
        detection = dependency.get("detection")
        if not isinstance(detection, Mapping):
            return []

        installations: list[DetectedInstallation] = []
        method = detection.get("method")

        if method in {"executable", "all"}:
            executable = detection.get("executable")
            if isinstance(executable, str):
                known_paths = self._known_paths(detection)
                installations.extend(
                    detect_executables(
                        executable,
                        version_args=detection.get("version_args", []),
                        known_paths=known_paths,
                    )
                )

        if method == "path":
            paths = self._known_paths({"known_paths": detection.get("paths")})
            installations.extend(detect_paths(paths))

        if method == "external":
            installations.append(
                DetectedInstallation(
                    version=None,
                    path=None,
                    detection_method="external_service",
                )
            )

        if method in {"python_package", "all"}:
            package_name = detection.get("python_package")
            if isinstance(package_name, str):
                installations.extend(detect_python_package(package_name))

        registry_name = detection.get("registry_name")
        if isinstance(registry_name, str):
            installations.extend(detect_installed_registry_entry(registry_name))

        package_manager = dependency.get("package_manager")
        if isinstance(package_manager, Mapping):
            for manager in detect_package_managers():
                package = package_manager.get(manager)
                if not isinstance(package, str):
                    continue
                version = query_package_version(manager, package)
                if version:
                    installations.append(
                        DetectedInstallation(
                            version=version,
                            path=None,
                            detection_method=f"package_manager:{manager}",
                        )
                    )

        return installations

    def _known_paths(self, detection: Mapping[str, Any]) -> Iterable[str]:
        known_paths = detection.get("known_paths")
        if not isinstance(known_paths, Mapping):
            return ()
        platform_name = "windows" if sys.platform.startswith("win") else "linux"
        paths = known_paths.get(platform_name)
        return tuple(path for path in paths if isinstance(path, str)) if isinstance(paths, list) else ()

    def _deduplicate_installations(
        self,
        installations: Iterable[DetectedInstallation],
    ) -> list[DetectedInstallation]:
        unique: dict[tuple[str | None, str | None], DetectedInstallation] = {}
        for installation in installations:
            path_key = str(installation.path) if installation.path else None
            key = (installation.version, path_key)
            unique.setdefault(key, installation)
        return list(unique.values())
