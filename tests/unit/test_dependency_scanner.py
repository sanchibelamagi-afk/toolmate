from pathlib import Path

from toolmate.core.dependency_scanner import DependencyScanner
from toolmate.core.compatibility_checker import CompatibilityChecker


def test_scans_missing_dependency(monkeypatch):
    monkeypatch.setattr(
        "toolmate.core.dependency_scanner.detect_executables",
        lambda *args, **kwargs: [],
    )
    monkeypatch.setattr(
        "toolmate.core.dependency_scanner.detect_python_package",
        lambda *args, **kwargs: [],
    )
    monkeypatch.setattr(
        "toolmate.core.dependency_scanner.detect_installed_registry_entry",
        lambda *args, **kwargs: [],
    )
    monkeypatch.setattr(
        "toolmate.core.dependency_scanner.detect_package_managers",
        lambda: (),
    )

    manifest = {
        "dependencies": [
            {
                "id": "ngspice",
                "name": "Ngspice",
                "detection": {
                    "method": "executable",
                    "executable": "ngspice",
                    "version_args": ["--version"],
                },
            }
        ]
    }

    result = DependencyScanner(manifest).scan()
    assert result[0].status == "missing"
    assert result[0].installations == ()


def test_scans_multiple_installations_without_duplicates(monkeypatch):
    from toolmate.core.models import DetectedInstallation

    detections = [
        DetectedInstallation(
            version="1.2.3",
            path=Path("/bin/tool"),
            detection_method="executable",
        ),
        DetectedInstallation(
            version="1.2.3",
            path=Path("/bin/tool"),
            detection_method="executable",
        ),
        DetectedInstallation(
            version="1.4.0",
            path=Path("/opt/tool"),
            detection_method="known_path",
        ),
    ]
    monkeypatch.setattr(
        "toolmate.core.dependency_scanner.detect_executables",
        lambda *args, **kwargs: detections,
    )
    monkeypatch.setattr(
        "toolmate.core.dependency_scanner.detect_package_managers",
        lambda: (),
    )

    manifest = {
        "dependencies": [
            {
                "id": "tool",
                "name": "Tool",
                "detection": {"method": "executable", "executable": "tool"},
            }
        ]
    }

    result = DependencyScanner(manifest).scan()
    assert result[0].status == "installed"
    assert len(result[0].installations) == 2


def test_scanner_reports_detection_errors(monkeypatch):
    monkeypatch.setattr(
        "toolmate.core.dependency_scanner.detect_executables",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("scan failed")),
    )
    monkeypatch.setattr(
        "toolmate.core.dependency_scanner.detect_package_managers",
        lambda: (),
    )

    manifest = {
        "dependencies": [
            {
                "id": "tool",
                "name": "Tool",
                "detection": {"method": "executable", "executable": "tool"},
            }
        ]
    }

    result = DependencyScanner(manifest).scan()
    assert result[0].status == "error"
    assert result[0].error == "scan failed"


def test_path_detection_marks_existing_toolchain_directory_installed(
    tmp_path,
    monkeypatch,
):
    pdk_path = tmp_path / "sky130A"
    pdk_path.mkdir()
    monkeypatch.setattr("toolmate.core.dependency_scanner.sys.platform", "linux")
    monkeypatch.setattr(
        "toolmate.core.dependency_scanner.detect_package_managers",
        lambda: (),
    )
    manifest = {
        "dependencies": [
            {
                "id": "skywater_sky130_pdk",
                "name": "SkyWater SKY130 PDK",
                "detection": {
                    "method": "path",
                    "paths": {"linux": [str(pdk_path)]},
                },
            }
        ]
    }

    inventory = DependencyScanner(manifest).scan()
    report = CompatibilityChecker(manifest).evaluate(inventory)

    assert inventory[0].status == "installed"
    assert report.entries[0].status == "installed"
    assert report.entries[0].path == pdk_path
    assert report.entries[0].installed_version is None


def test_external_service_is_reported_as_unknown_not_missing(monkeypatch):
    monkeypatch.setattr(
        "toolmate.core.dependency_scanner.detect_package_managers",
        lambda: (),
    )
    manifest = {
        "dependencies": [
            {
                "id": "makerchip",
                "name": "Makerchip",
                "detection": {"method": "external", "url": "https://makerchip.com/"},
            }
        ]
    }

    inventory = DependencyScanner(manifest).scan()
    result = CompatibilityChecker(manifest).evaluate(inventory).entries[0]

    assert inventory[0].status == "unknown"
    assert result.status == "unknown"
    assert "cannot be detected locally" in result.detail


def test_scanner_marks_platform_unsupported_dependencies(monkeypatch):
    monkeypatch.setattr("toolmate.core.dependency_scanner.sys.platform", "win32")
    manifest = {
        "dependencies": [
            {
                "id": "pdk",
                "name": "PDK",
                "platforms": {
                    "windows": {"supported": False},
                    "linux": {"supported": True},
                },
                "detection": {"method": "path", "paths": {"windows": []}},
            }
        ]
    }

    inventory = DependencyScanner(manifest).scan()
    result = CompatibilityChecker(manifest).evaluate(inventory).entries[0]

    assert inventory[0].status == "unsupported"
    assert result.status == "unsupported"
    assert "not supported" in result.detail
