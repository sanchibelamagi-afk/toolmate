from collections.abc import Callable
from threading import Event

from toolmate.installers.base_installer import BaseInstaller, InstallationResult


class ChocolateyInstaller(BaseInstaller):
    def install(
        self,
        package_id: str,
        on_output: Callable[[str], None] | None = None,
        cancel_event: Event | None = None,
    ) -> InstallationResult:
        return self.execute(["choco", "install", package_id, "-y"], on_output, cancel_event)
