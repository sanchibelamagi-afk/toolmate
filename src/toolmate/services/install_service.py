from collections.abc import Callable
import shutil
import sys
from typing import Any, Mapping

from src.toolmate.core.manifest_manager import ManifestManager
from src.toolmate.installers.apt_installer import AptInstaller
from src.toolmate.installers.base_installer import InstallationResult
from src.toolmate.installers.chocolatey_installer import ChocolateyInstaller
from src.toolmate.installers.winget_installer import WingetInstaller


class InstallService:
    def __init__(self, manifest_path: str) -> None:
        self.manifest = ManifestManager(manifest_path).load()

    def plan(self, dependency_id: str) -> tuple[tuple[str, ...], str]:
        dependency = self._dependency(dependency_id)
        package_manager = dependency.get("package_manager")
        if not isinstance(package_manager, Mapping):
            package_manager = {}

        if sys.platform.startswith("win"):
            if shutil.which("winget") and package_manager.get("winget"):
                command = ("winget", "install", "--id", str(package_manager["winget"]), "--exact", "--accept-package-agreements", "--accept-source-agreements")
                return command, f"winget package {package_manager['winget']}"
            if shutil.which("choco") and package_manager.get("choco"):
                command = ("choco", "install", str(package_manager["choco"]), "-y")
                return command, f"Chocolatey package {package_manager['choco']}"
        if shutil.which("apt") and package_manager.get("apt"):
            return ("apt-get", "install", "-y", str(package_manager["apt"])), f"APT package {package_manager['apt']}"
        installation = dependency.get("installation")
        manual_url = installation.get("manual_url") if isinstance(installation, Mapping) else None
        if manual_url:
            return (f"Manual download: {manual_url}",), "Manual installation guidance"
        return (), "No supported installation source is configured for this platform"

    def execute(
        self,
        dependency_id: str,
        approved: bool,
        on_output: Callable[[str], None] | None = None,
    ) -> InstallationResult:
        if not approved:
            raise PermissionError("Installation requires explicit user approval.")

        dependency = self._dependency(dependency_id)
        package_manager = dependency.get("package_manager")
        if not isinstance(package_manager, Mapping):
            package_manager = {}

        if sys.platform.startswith("win"):
            if shutil.which("winget") and package_manager.get("winget"):
                return WingetInstaller().install(str(package_manager["winget"]), on_output)
            if shutil.which("choco") and package_manager.get("choco"):
                return ChocolateyInstaller().install(str(package_manager["choco"]), on_output)
        if shutil.which("apt") and package_manager.get("apt"):
            return AptInstaller().install(str(package_manager["apt"]), on_output)

        installation = dependency.get("installation")
        manual_url = installation.get("manual_url") if isinstance(installation, Mapping) else None
        if manual_url:
            raise RuntimeError(
                f"No automated package manager is available. Follow the manual "
                f"installation guidance: {manual_url}"
            )
        raise RuntimeError("No supported installation source is available.")

    def _dependency(self, dependency_id: str) -> Mapping[str, Any]:
        for dependency in self.manifest["dependencies"]:
            if dependency.get("id") == dependency_id:
                return dependency
        raise KeyError(f"Unknown dependency: {dependency_id}")
