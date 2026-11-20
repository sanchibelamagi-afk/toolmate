from collections.abc import Callable
from dataclasses import dataclass
import subprocess


@dataclass(frozen=True)
class InstallationResult:
    command: tuple[str, ...]
    exit_code: int
    output: str

    @property
    def succeeded(self) -> bool:
        return self.exit_code == 0


class BaseInstaller:
    def execute(
        self,
        command: list[str],
        on_output: Callable[[str], None] | None = None,
    ) -> InstallationResult:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        chunks: list[str] = []
        if process.stdout is not None:
            for line in process.stdout:
                chunks.append(line)
                if on_output is not None:
                    on_output(line.rstrip())
        exit_code = process.wait()
        return InstallationResult(
            command=tuple(command),
            exit_code=exit_code,
            output="".join(chunks),
        )
