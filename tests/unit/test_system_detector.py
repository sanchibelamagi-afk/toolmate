from pathlib import Path

from toolmate.core.system_detector import detect_system_info


def test_detect_system_info_returns_required_fields(monkeypatch):
    monkeypatch.setattr(
        "toolmate.core.system_detector.detect_package_managers",
        lambda: ("apt",),
    )
    monkeypatch.setattr(
        "toolmate.core.system_detector.locate_esim",
        lambda: Path("/tmp/esim"),
    )

    info = detect_system_info()

    assert info.operating_system in {"Windows", "Linux", "macOS"}
    assert info.os_version
    assert info.architecture
    assert isinstance(info.administrator, bool)
    assert info.package_managers == ("apt",)
    assert info.esim_path == Path("/tmp/esim")


def test_detect_system_info_identifies_macos(monkeypatch):
    monkeypatch.setattr("toolmate.core.system_detector.sys.platform", "darwin")
    monkeypatch.setattr(
        "toolmate.core.system_detector.detect_package_managers",
        lambda: ("brew",),
    )
    monkeypatch.setattr(
        "toolmate.core.system_detector.locate_esim",
        lambda: Path("/Users/test/eSim"),
    )
    monkeypatch.setattr(
        "toolmate.core.system_detector.macos.is_administrator",
        lambda: False,
    )

    info = detect_system_info()

    assert info.operating_system == "macOS"
    assert info.package_managers == ("brew",)
    assert info.esim_path == Path("/Users/test/eSim")
