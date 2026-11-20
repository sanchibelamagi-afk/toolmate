from pathlib import Path

from src.toolmate.core.dependency_scanner import DependencyScanner


def test_scans_missing_dependency(monkeypatch):
    monkeypatch.setattr(
        "src.toolmate.core.dependency_scanner.detect_executables",
        lambda *args, **kwargs: [],
    )
    monkeypatch.setattr(
        "src.toolmate.core.dependency_scanner.detect_python_package",
        lambda *args, **kwargs: [],
    )
    monkeypatch.setattr(
        "src.toolmate.core.dependency_scanner.detect_installed_registry_entry",
        lambda *args, **kwargs: [],
    )
    monkeypatch.setattr(
        "src.toolmate.core.dependency_scanner.detect_package_managers",
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
    from src.toolmate.core.models import DetectedInstallation

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
        "src.toolmate.core.dependency_scanner.detect_executables",
        lambda *args, **kwargs: detections,
    )
    monkeypatch.setattr(
        "src.toolmate.core.dependency_scanner.detect_package_managers",
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
        "src.toolmate.core.dependency_scanner.detect_executables",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("scan failed")),
    )
    monkeypatch.setattr(
        "src.toolmate.core.dependency_scanner.detect_package_managers",
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
