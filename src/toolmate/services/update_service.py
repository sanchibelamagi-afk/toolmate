import json
import re
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from threading import Event
from typing import Any, Mapping

from toolmate.core.manifest_manager import ManifestManager
from toolmate.installers.apt_installer import AptInstaller
from toolmate.installers.base_installer import BaseInstaller, InstallationResult
from toolmate.installers.pacman_installer import PacmanInstaller


class UpdateService:
    def __init__(self, manifest_path: str | Path) -> None:
        self.manifest = ManifestManager(manifest_path).load()

    def check_available(self) -> dict[str, str]:
        manager = self._available_manager()
        if manager is None:
            raise RuntimeError("No supported update package manager is available.")

        packages = self._package_dependencies(manager)
        if not packages:
            raise RuntimeError(
                f"No manifest dependencies have a {manager} package mapping."
            )
        command = {
            "winget": [
                "winget",
                "upgrade",
                "--accept-source-agreements",
                "--disable-interactivity",
            ],
            "apt": ["apt", "list", "--upgradable"],
            "pacman": ["pacman", "-Qu"],
            "brew": ["brew", "outdated", "--json=v2"],
        }[manager]
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise RuntimeError(f"Could not check {manager} updates: {exc}") from exc

        output = result.stdout.strip()
        if result.returncode != 0:
            error_output = "\n".join((result.stdout, result.stderr)).strip()
            raise RuntimeError(
                f"{manager} update check failed with exit code "
                f"{result.returncode}: {error_output}"
            )
        available = self._parse_updates(manager, output, packages)
        return {
            dependency_id: available[package.casefold()]
            for package, dependency_id in packages.items()
            if package.casefold() in available
        }

    def plan(self, dependency_id: str) -> tuple[tuple[str, ...], str]:
        manager = self._available_manager()
        if manager is None:
            raise RuntimeError("No supported update package manager is available.")
        package = self._package_for_dependency(manager, dependency_id)
        if package is None:
            raise RuntimeError(
                f"No {manager} package is configured for {dependency_id}."
            )
        if manager == "winget":
            command = (
                "winget",
                "upgrade",
                "--id",
                package,
                "--exact",
                "--accept-package-agreements",
                "--accept-source-agreements",
                "--disable-interactivity",
            )
        elif manager == "apt":
            command = tuple(AptInstaller.upgrade_command_for(package))
        elif manager == "pacman":
            command = tuple(PacmanInstaller.command_for(package))
        else:
            command = ("brew", "upgrade", package)
        return command, f"{manager} package {package}"

    def execute(
        self,
        dependency_id: str,
        approved: bool,
        on_output: Callable[[str], None] | None = None,
        cancel_event: Event | None = None,
    ) -> InstallationResult:
        if not approved:
            raise PermissionError("Updates require explicit user approval.")
        command, _ = self.plan(dependency_id)
        return BaseInstaller().execute(list(command), on_output, cancel_event)

    def _available_manager(self) -> str | None:
        if sys.platform.startswith("win"):
            return "winget" if shutil.which("winget") else None
        if sys.platform == "darwin":
            return "brew" if shutil.which("brew") else None
        if sys.platform.startswith("linux"):
            if shutil.which("apt"):
                return "apt"
            if shutil.which("pacman"):
                return "pacman"
        return None

    def _package_dependencies(self, manager: str) -> dict[str, str]:
        result: dict[str, str] = {}
        for dependency in self.manifest["dependencies"]:
            package = self._package_id(dependency, manager)
            if package:
                result[package] = str(dependency["id"])
        return result

    def _package_for_dependency(
        self,
        manager: str,
        dependency_id: str,
    ) -> str | None:
        for dependency in self.manifest["dependencies"]:
            if dependency.get("id") == dependency_id:
                return self._package_id(dependency, manager)
        raise KeyError(f"Unknown dependency: {dependency_id}")

    @staticmethod
    def _package_id(dependency: Mapping[str, Any], manager: str) -> str | None:
        package_managers = dependency.get("package_manager")
        if not isinstance(package_managers, Mapping):
            return None
        package = package_managers.get(manager)
        return package if isinstance(package, str) and package else None

    @staticmethod
    def _parse_updates(
        manager: str,
        output: str,
        packages: Mapping[str, str],
    ) -> dict[str, str]:
        if manager == "apt":
            available: dict[str, str] = {}
            for line in output.splitlines():
                match = re.match(r"^([^/\s]+)/\S+\s+(\S+).*\[upgradable from:", line)
                if match:
                    available[match.group(1).casefold()] = match.group(2)
            return available

        if manager == "pacman":
            available = {}
            for line in output.splitlines():
                match = re.match(r"^(\S+)\s+\S+\s+->\s+(\S+)\s*$", line.strip())
                if match:
                    available[match.group(1).casefold()] = match.group(2)
            return available

        if manager == "brew":
            try:
                data = json.loads(output or "{}")
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"Homebrew returned invalid update data: {exc}") from exc
            available = {}
            for kind in ("formulae", "casks"):
                items = data.get(kind, [])
                if not isinstance(items, list):
                    continue
                for item in items:
                    if not isinstance(item, Mapping):
                        continue
                    name = item.get("name")
                    version = item.get("current") or item.get("current_version")
                    if isinstance(name, str) and isinstance(version, str):
                        available[name.casefold()] = version
            return available

        if manager == "winget":
            available = {}
            expected = {package.casefold() for package in packages}
            for line in output.splitlines():
                tokens = line.split()
                lowered = [token.casefold() for token in tokens]
                for package in expected.intersection(lowered):
                    package_index = lowered.index(package)
                    versions = [
                        token
                        for token in tokens[package_index + 1 :]
                        if re.match(r"^\d[\w.+-]*$", token)
                    ]
                    if len(versions) >= 2:
                        available[package] = versions[1]
                    else:
                        available[package] = "Available"
            return available

        raise ValueError(f"Unsupported package manager: {manager}")
