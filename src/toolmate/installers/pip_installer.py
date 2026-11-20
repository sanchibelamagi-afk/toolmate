from collections.abc import Callable
import sys
from threading import Event

from toolmate.installers.base_installer import BaseInstaller, InstallationResult


class PipInstaller(BaseInstaller):
    def install(
        self,
        package: str,
        on_output: Callable[[str], None] | None = None,
        cancel_event: Event | None = None,
    ) -> InstallationResult:
        return self.execute(
            [sys.executable, "-m", "pip", "install", package],
            on_output,
            cancel_event,
        )
