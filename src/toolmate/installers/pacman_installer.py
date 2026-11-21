import os
from collections.abc import Callable
from threading import Event

from toolmate.installers.base_installer import BaseInstaller, InstallationResult


def _requires_sudo() -> bool:
    return hasattr(os, "geteuid") and os.geteuid() != 0


class PacmanInstaller(BaseInstaller):
    @staticmethod
    def command_for(package: str) -> list[str]:
        command = ["pacman", "-S", "--noconfirm", "--needed", package]
        if _requires_sudo():
            command.insert(0, "sudo")
        return command

    def install(
        self,
        package: str,
        on_output: Callable[[str], None] | None = None,
        cancel_event: Event | None = None,
    ) -> InstallationResult:
        return self.execute(self.command_for(package), on_output, cancel_event)
