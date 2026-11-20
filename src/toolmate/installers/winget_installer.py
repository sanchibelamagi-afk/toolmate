from collections.abc import Callable
from threading import Event

from toolmate.installers.base_installer import BaseInstaller, InstallationResult


class WingetInstaller(BaseInstaller):
    def install(
        self,
        package_id: str,
        on_output: Callable[[str], None] | None = None,
        cancel_event: Event | None = None,
    ) -> InstallationResult:
        return self.execute(
            ["winget", "install", "--id", package_id, "--exact", "--accept-package-agreements", "--accept-source-agreements"],
            on_output,
            cancel_event,
        )
