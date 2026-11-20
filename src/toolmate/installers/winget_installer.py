from collections.abc import Callable

from src.toolmate.installers.base_installer import BaseInstaller, InstallationResult


class WingetInstaller(BaseInstaller):
    def install(
        self,
        package_id: str,
        on_output: Callable[[str], None] | None = None,
    ) -> InstallationResult:
        return self.execute(
            ["winget", "install", "--id", package_id, "--exact", "--accept-package-agreements", "--accept-source-agreements"],
            on_output,
        )
