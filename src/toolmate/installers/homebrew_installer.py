from collections.abc import Callable
from threading import Event

from toolmate.installers.base_installer import BaseInstaller, InstallationResult


class HomebrewInstaller(BaseInstaller):
    def install(
        self,
        package: str,
        on_output: Callable[[str], None] | None = None,
        cancel_event: Event | None = None,
    ) -> InstallationResult:
        return self.execute(["brew", "install", package], on_output, cancel_event)
