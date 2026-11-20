import hashlib
import threading

import pytest

from toolmate.installers.download_installer import DownloadInstaller


class FakeResponse:
    headers = {"content-length": "7"}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def raise_for_status(self):
        return None

    def iter_content(self, chunk_size):
        yield b"payload"


def test_download_verifies_checksum_and_reports_progress(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "toolmate.installers.download_installer.requests.get",
        lambda *args, **kwargs: FakeResponse(),
    )
    progress = []
    destination = tmp_path / "asset.bin"

    result = DownloadInstaller().download(
        "https://downloads.example/asset.bin",
        destination,
        hashlib.sha256(b"payload").hexdigest(),
        on_progress=lambda downloaded, total: progress.append((downloaded, total)),
    )

    assert result.read_bytes() == b"payload"
    assert progress == [(7, 7)]


def test_download_rejects_checksum_mismatch(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "toolmate.installers.download_installer.requests.get",
        lambda *args, **kwargs: FakeResponse(),
    )

    with pytest.raises(ValueError, match="SHA-256"):
        DownloadInstaller().download(
            "https://downloads.example/asset.bin",
            tmp_path / "asset.bin",
            "0" * 64,
        )
    assert not (tmp_path / "asset.bin").exists()


def test_download_requires_https_and_checksum(tmp_path):
    installer = DownloadInstaller()

    with pytest.raises(ValueError, match="HTTPS"):
        installer.download("http://downloads.example/asset.bin", tmp_path / "asset.bin", "0" * 64)
    with pytest.raises(ValueError, match="SHA-256"):
        installer.download("https://downloads.example/asset.bin", tmp_path / "asset.bin", "invalid")


def test_download_can_be_cancelled(monkeypatch, tmp_path):
    cancel_event = threading.Event()
    cancel_event.set()
    monkeypatch.setattr(
        "toolmate.installers.download_installer.requests.get",
        lambda *args, **kwargs: FakeResponse(),
    )

    with pytest.raises(InterruptedError, match="cancelled"):
        DownloadInstaller().download(
            "https://downloads.example/asset.bin",
            tmp_path / "asset.bin",
            hashlib.sha256(b"payload").hexdigest(),
            cancel_event=cancel_event,
        )
    assert list(tmp_path.iterdir()) == []
