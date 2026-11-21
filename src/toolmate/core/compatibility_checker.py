from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Mapping

from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import InvalidVersion, Version

from toolmate.core.models import (
    CompatibilityReport,
    CompatibilityResult,
    DependencyInventoryEntry,
)


class CompatibilityChecker:
    def __init__(self, manifest: Mapping[str, Any]) -> None:
        dependencies = manifest.get("dependencies")
        if not isinstance(dependencies, list):
            raise ValueError("Manifest dependencies must be a list")
        self.dependencies = {
            str(dependency["id"]): dependency
            for dependency in dependencies
            if isinstance(dependency, dict) and dependency.get("id")
        }

    def evaluate(
        self,
        inventory: list[DependencyInventoryEntry],
    ) -> CompatibilityReport:
        results = [
            self._evaluate_entry(entry)
            for entry in inventory
        ]
        return CompatibilityReport(entries=tuple(results))

    def _evaluate_entry(
        self,
        entry: DependencyInventoryEntry,
    ) -> CompatibilityResult:
        dependency = self.dependencies.get(entry.id)
        if dependency is None:
            return CompatibilityResult(
                id=entry.id,
                name=entry.name,
                status="unknown",
                installed_version=None,
                path=None,
                detail="Dependency is not defined in the manifest.",
            )

        if entry.status == "missing":
            return CompatibilityResult(
                id=entry.id,
                name=entry.name,
                status="missing",
                installed_version=None,
                path=None,
                detail="Dependency was not detected.",
            )
        if entry.status == "unsupported":
            return CompatibilityResult(
                id=entry.id,
                name=entry.name,
                status="unsupported",
                installed_version=None,
                path=None,
                detail="Dependency is not supported on this platform.",
            )
        if entry.status == "error":
            return CompatibilityResult(
                id=entry.id,
                name=entry.name,
                status="failed",
                installed_version=None,
                path=None,
                detail=entry.error or "Dependency detection failed.",
            )

        installations = [item for item in entry.installations if item.version is not None]
        if not installations:
            path_installations = [
                item for item in entry.installations
                if item.detection_method == "path" and item.path is not None
            ]
            if entry.status == "installed" and path_installations:
                return CompatibilityResult(
                    id=entry.id,
                    name=entry.name,
                    status="installed",
                    installed_version=None,
                    path=path_installations[0].path,
                    detail="Installation path exists; no version command is available.",
                )
            if any(
                item.detection_method == "external_service"
                for item in entry.installations
            ):
                return CompatibilityResult(
                    id=entry.id,
                    name=entry.name,
                    status="unknown",
                    installed_version=None,
                    path=None,
                    detail="Online service availability cannot be detected locally.",
                )
            return CompatibilityResult(
                id=entry.id,
                name=entry.name,
                status="unknown",
                installed_version=None,
                path=entry.installations[0].path if entry.installations else None,
                detail="A version could not be determined.",
            )

        for installation in installations:
            misconfigured = self._misconfigured_path(installation.path)
            if misconfigured:
                return CompatibilityResult(
                    id=entry.id,
                    name=entry.name,
                    status="misconfigured",
                    installed_version=installation.version,
                    path=installation.path,
                    detail=f"Detected path is invalid: {installation.path}",
                )

        installation = self._preferred_installation(installations)
        version_text = installation.version
        constraints = self._get_constraints(dependency)

        try:
            installed_version = Version(str(version_text).strip())
        except InvalidVersion:
            return CompatibilityResult(
                id=entry.id,
                name=entry.name,
                status="unknown",
                installed_version=version_text,
                path=installation.path,
                detail=f"Version is not recognizable: {version_text}",
            )

        minimum = constraints.get("minimum")
        if minimum:
            try:
                if installed_version < Version(str(minimum)):
                    return CompatibilityResult(
                        id=entry.id,
                        name=entry.name,
                        status="outdated",
                        installed_version=version_text,
                        path=installation.path,
                        detail=f"Installed version is below minimum {minimum}.",
                    )
            except InvalidVersion:
                return CompatibilityResult(
                    id=entry.id,
                    name=entry.name,
                    status="unknown",
                    installed_version=version_text,
                    path=installation.path,
                    detail=f"Manifest minimum version is invalid: {minimum}",
                )

        maximum = constraints.get("maximum")
        if maximum:
            try:
                if installed_version > Version(str(maximum)):
                    return CompatibilityResult(
                        id=entry.id,
                        name=entry.name,
                        status="incompatible",
                        installed_version=version_text,
                        path=installation.path,
                        detail=f"Installed version exceeds maximum {maximum}.",
                    )
            except InvalidVersion:
                return CompatibilityResult(
                    id=entry.id,
                    name=entry.name,
                    status="unknown",
                    installed_version=version_text,
                    path=installation.path,
                    detail=f"Manifest maximum version is invalid: {maximum}",
                )

        excluded = constraints.get("excluded")
        if isinstance(excluded, list):
            for excluded_specifier in excluded:
                try:
                    normalized_specifier = self._normalize_specifier(str(excluded_specifier))
                    if installed_version in SpecifierSet(normalized_specifier):
                        return CompatibilityResult(
                            id=entry.id,
                            name=entry.name,
                            status="incompatible",
                            installed_version=version_text,
                            path=installation.path,
                            detail=f"Version is excluded by manifest rule {excluded_specifier}.",
                        )
                except InvalidSpecifier:
                    return CompatibilityResult(
                        id=entry.id,
                        name=entry.name,
                        status="unknown",
                        installed_version=version_text,
                        path=installation.path,
                        detail=f"Manifest exclusion is invalid: {excluded_specifier}",
                    )

        return CompatibilityResult(
            id=entry.id,
            name=entry.name,
            status="installed",
            installed_version=version_text,
            path=installation.path,
            detail="Detected version satisfies the manifest constraints.",
        )

    def _get_constraints(self, dependency: Mapping[str, Any]) -> Mapping[str, Any]:
        version = dependency.get("version")
        return version if isinstance(version, Mapping) else {}

    def _preferred_installation(self, installations: list[Any]) -> Any:
        with_paths = [item for item in installations if item.path is not None]
        return with_paths[0] if with_paths else installations[0]

    def _misconfigured_path(self, path: Path | None) -> bool:
        if path is None:
            return False
        if not path.exists():
            return True
        if sys.platform.startswith("win") and path.suffix.lower() not in {
            ".exe",
            ".cmd",
            ".bat",
        }:
            return path.is_file()
        return False

    def _normalize_specifier(self, specifier: str) -> str:
        specifier = specifier.strip()
        if not specifier:
            raise InvalidSpecifier("Empty specifier")
        if specifier.startswith(("==", "!=", "<=", ">=", "<", ">", "~=", "===")):
            return specifier
        if "*" in specifier:
            return f"=={specifier}"
        return f"=={specifier}"
