from __future__ import annotations

import hashlib
import hmac
import os
from pathlib import Path
import re
import tempfile
from collections.abc import Callable
from threading import Event
from urllib.parse import urlparse

import requests


class DownloadInstaller:
    def download(
        self,
        url: str,
        destination: str | Path,
        expected_sha256: str,
        cancel_event: Event | None = None,
        on_progress: Callable[[int, int], None] | None = None,
    ) -> Path:
        parsed_url = urlparse(url)
        if parsed_url.scheme != "https":
            raise ValueError("Downloads require an HTTPS URL.")
        if not re.fullmatch(r"[a-fA-F0-9]{64}", expected_sha256):
            raise ValueError("A valid SHA-256 checksum is required.")

        target = Path(destination)
        if target.name in {"", ".", ".."} or target.name != Path(target.name).name:
            raise ValueError("Download destination must be a file name.")
        target.parent.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256()
        temporary_path: Path | None = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=target.parent,
                prefix=f".{target.name}.",
                suffix=".part",
                delete=False,
            ) as output_file:
                temporary_path = Path(output_file.name)
                downloaded = 0
                with requests.get(url, stream=True, timeout=(10, 30)) as response:
                    response.raise_for_status()
                    total = int(response.headers.get("content-length", 0))
                    for chunk in response.iter_content(chunk_size=64 * 1024):
                        if cancel_event is not None and cancel_event.is_set():
                            raise InterruptedError("Download cancelled.")
                        if not chunk:
                            continue
                        output_file.write(chunk)
                        digest.update(chunk)
                        downloaded += len(chunk)
                        if on_progress is not None:
                            on_progress(downloaded, total)
                output_file.flush()
                os.fsync(output_file.fileno())

            if not hmac.compare_digest(digest.hexdigest().lower(), expected_sha256.lower()):
                raise ValueError("Downloaded file SHA-256 does not match the manifest.")
            temporary_path.replace(target)
            return target
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()
