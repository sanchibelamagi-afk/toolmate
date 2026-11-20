from collections.abc import Callable

from src.toolmate.installers.base_installer import BaseInstaller, InstallationResult


class ChocolateyInstaller(BaseInstaller):
    def install(
        self,
        package_id: str,
        on_output: Callable[[str], None] | None = None,
    ) -> InstallationResult:
        return self.execute(["choco", "install", package_id, "-y"], on_output)
