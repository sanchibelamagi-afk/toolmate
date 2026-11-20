from collections.abc import Callable
from dataclasses import dataclass
from queue import Empty, Queue
import subprocess
from threading import Event, Thread


@dataclass(frozen=True)
class InstallationResult:
    command: tuple[str, ...]
    exit_code: int
    output: str
    cancelled: bool = False

    @property
    def succeeded(self) -> bool:
        return self.exit_code == 0 and not self.cancelled


class BaseInstaller:
    def execute(
        self,
        command: list[str],
        on_output: Callable[[str], None] | None = None,
        cancel_event: Event | None = None,
    ) -> InstallationResult:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        chunks: list[str] = []
        output_queue: Queue[str | None] = Queue()

        def read_output() -> None:
            if process.stdout is not None:
                for line in process.stdout:
                    output_queue.put(line)
            output_queue.put(None)

        reader = Thread(target=read_output, daemon=True)
        reader.start()
        cancelled = False
        output_finished = False
        while not output_finished:
            if cancel_event is not None and cancel_event.is_set() and process.poll() is None:
                cancelled = True
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()

            try:
                line = output_queue.get(timeout=0.1)
            except Empty:
                continue
            if line is None:
                output_finished = True
            else:
                chunks.append(line)
                if on_output is not None:
                    on_output(line.rstrip())

        exit_code = process.wait()
        reader.join()
        return InstallationResult(
            command=tuple(command),
            exit_code=exit_code,
            output="".join(chunks),
            cancelled=cancelled,
        )
