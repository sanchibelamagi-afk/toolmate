import sys
import threading
import time

from toolmate.installers.base_installer import BaseInstaller


def test_running_command_can_be_cancelled():
    cancel_event = threading.Event()
    command = [
        sys.executable,
        "-c",
        "import time; print('started', flush=True); time.sleep(10)",
    ]

    def request_cancel():
        time.sleep(0.2)
        cancel_event.set()

    cancel_thread = threading.Thread(target=request_cancel, daemon=True)
    cancel_thread.start()
    result = BaseInstaller().execute(command, cancel_event=cancel_event)
    cancel_thread.join()

    assert result.cancelled is True
    assert result.succeeded is False
    assert "started" in result.output
