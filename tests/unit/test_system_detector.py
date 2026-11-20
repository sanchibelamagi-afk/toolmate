from pathlib import Path

from src.toolmate.core.system_detector import detect_system_info


def test_detect_system_info_returns_required_fields(monkeypatch):
    monkeypatch.setattr(
        "src.toolmate.core.system_detector.detect_package_managers",
        lambda: ("apt",),
    )
    monkeypatch.setattr(
        "src.toolmate.core.system_detector.locate_esim",
        lambda: Path("/tmp/esim"),
    )

    info = detect_system_info()

    assert info.operating_system in {"Windows", "Linux"}
    assert info.os_version
    assert info.architecture
    assert isinstance(info.administrator, bool)
    assert info.package_managers == ("apt",)
    assert info.esim_path == Path("/tmp/esim")
