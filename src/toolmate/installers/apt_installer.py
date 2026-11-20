import os
from collections.abc import Callable

from src.toolmate.installers.base_installer import BaseInstaller, InstallationResult


class AptInstaller(BaseInstaller):
    def install(
        self,
        package: str,
        on_output: Callable[[str], None] | None = None,
    ) -> InstallationResult:
        command = ["apt-get", "install", "-y", package]
        if os.geteuid() != 0:
            command.insert(0, "sudo")
        return self.execute(command, on_output)
