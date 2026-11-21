from collections.abc import Callable
import shutil
import sys
from pathlib import Path
from threading import Event
from typing import Any, Mapping

from toolmate.core.manifest_manager import ManifestManager
from toolmate.installers.apt_installer import AptInstaller
from toolmate.installers.base_installer import InstallationResult
from toolmate.installers.chocolatey_installer import ChocolateyInstaller
from toolmate.installers.download_installer import DownloadInstaller
from toolmate.installers.homebrew_installer import HomebrewInstaller
from toolmate.installers.pacman_installer import PacmanInstaller
from toolmate.installers.winget_installer import WingetInstaller


class InstallService:
    def __init__(self, manifest_path: str) -> None:
        self.manifest = ManifestManager(manifest_path).load()

    def plan(self, dependency_id: str) -> tuple[tuple[str, ...], str]:
        dependency = self._dependency(dependency_id)
        package_manager = self._package_manager_install(dependency)
        if package_manager is not None:
            manager, package_id = package_manager
            if manager == "winget":
                command = (
                    "winget",
                    "install",
                    "--id",
                    package_id,
                    "--exact",
                    "--accept-package-agreements",
                    "--accept-source-agreements",
                )
                return command, f"winget package {package_id}"
            if manager == "choco":
                return ("choco", "install", package_id, "-y"), f"Chocolatey package {package_id}"
            if manager == "pacman":
                return (
                    tuple(PacmanInstaller.command_for(package_id)),
                    f"pacman package {package_id}",
                )
            if manager == "brew":
                return ("brew", "install", package_id), f"Homebrew package {package_id}"
            return tuple(AptInstaller.command_for(package_id)), f"APT package {package_id}"
        installation = dependency.get("installation")
        download = installation.get("download") if isinstance(installation, Mapping) else None
        if isinstance(download, Mapping):
            return (
                f"Download and verify {download.get('filename', 'package')}",
                f"SHA-256 verification required before use ({download.get('url', '')})",
            )
        manual_url = installation.get("manual_url") if isinstance(installation, Mapping) else None
        if manual_url:
            return (f"Manual download: {manual_url}",), "Manual installation guidance"
        return (), "No supported installation source is configured for this platform"

    def can_install_automatically(self, dependency_id: str) -> bool:
        return self._package_manager_install(self._dependency(dependency_id)) is not None

    @staticmethod
    def _package_manager_install(
        dependency: Mapping[str, Any],
    ) -> tuple[str, str] | None:
        package_manager = dependency.get("package_manager")
        if not isinstance(package_manager, Mapping):
            package_manager = {}

        if sys.platform.startswith("win"):
            if shutil.which("winget") and package_manager.get("winget"):
                return "winget", str(package_manager["winget"])
            if shutil.which("choco") and package_manager.get("choco"):
                return "choco", str(package_manager["choco"])
        if sys.platform.startswith("linux"):
            if shutil.which("apt") and package_manager.get("apt"):
                return "apt", str(package_manager["apt"])
            if shutil.which("pacman") and package_manager.get("pacman"):
                return "pacman", str(package_manager["pacman"])
        if sys.platform == "darwin":
            if shutil.which("brew") and package_manager.get("brew"):
                return "brew", str(package_manager["brew"])
        return None

    def execute(
        self,
        dependency_id: str,
        approved: bool,
        on_output: Callable[[str], None] | None = None,
        cancel_event: Event | None = None,
    ) -> InstallationResult:
        if not approved:
            raise PermissionError("Installation requires explicit user approval.")

        dependency = self._dependency(dependency_id)
        package_manager = self._package_manager_install(dependency)
        if package_manager is not None:
            manager, package_id = package_manager
            if manager == "winget":
                return WingetInstaller().install(package_id, on_output, cancel_event)
            if manager == "choco":
                return ChocolateyInstaller().install(package_id, on_output, cancel_event)
            if manager == "pacman":
                return PacmanInstaller().install(package_id, on_output, cancel_event)
            if manager == "brew":
                return HomebrewInstaller().install(package_id, on_output, cancel_event)
            return AptInstaller().install(
                package_id, on_output, cancel_event
            )

        installation = dependency.get("installation")
        download = installation.get("download") if isinstance(installation, Mapping) else None
        if isinstance(download, Mapping):
            url = download.get("url")
            filename = download.get("filename")
            checksum = download.get("sha256")
            if not all(isinstance(value, str) and value for value in (url, filename, checksum)):
                raise ValueError("Manifest downloads require url, filename, and sha256.")
            if Path(filename).name != filename:
                raise ValueError("Manifest download filename must not contain a path.")
            try:
                output_path = DownloadInstaller().download(
                    url,
                    Path("cache") / filename,
                    checksum,
                    cancel_event=cancel_event,
                    on_progress=(
                        lambda downloaded, total: on_output(
                            f"Download: {downloaded} / {total} bytes"
                        )
                        if on_output is not None
                        else None
                    ),
                )
            except InterruptedError:
                return InstallationResult(
                    command=("download", url),
                    exit_code=1,
                    output="Download cancelled.",
                    cancelled=True,
                )
            if on_output is not None:
                on_output(f"Downloaded and verified package: {output_path}")
            return InstallationResult(
                command=("download", url),
                exit_code=0,
                output=f"Downloaded and SHA-256 verified to {output_path}",
            )
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
