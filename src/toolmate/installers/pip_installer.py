from collections.abc import Callable
import sys

from src.toolmate.installers.base_installer import BaseInstaller, InstallationResult


class PipInstaller(BaseInstaller):
    def install(
        self,
        package: str,
        on_output: Callable[[str], None] | None = None,
    ) -> InstallationResult:
        return self.execute([sys.executable, "-m", "pip", "install", package], on_output)
