import pytest

from toolmate.core.models import (
    CompatibilityReport,
    CompatibilityResult,
    SystemInfo,
)
from toolmate.integration.esim import EsimIntegrationService


def test_esim_report_validates_roots_and_configured_dependency_paths(
    tmp_path,
    monkeypatch,
):
    esim_root = tmp_path / "esim"
    esim_root.mkdir()
    installed_tool = tmp_path / "ngspice"
    installed_tool.write_text("tool", encoding="utf-8")
    report = CompatibilityReport(
        entries=(
            CompatibilityResult(
                id="ngspice",
                name="Ngspice",
                status="installed",
                installed_version="42",
                path=installed_tool,
                detail="Detected.",
            ),
            CompatibilityResult(
                id="kicad",
                name="KiCad",
                status="missing",
                installed_version=None,
                path=None,
                detail="Not detected.",
            ),
        )
    )
    monkeypatch.setattr(
        "toolmate.integration.esim.detect_system_info",
        lambda: SystemInfo(
            operating_system="Linux",
            os_version="Test OS",
            architecture="x86_64",
            package_managers=("apt",),
            administrator=False,
            esim_path=None,
        ),
    )
    monkeypatch.setattr(
        "toolmate.integration.esim.ScanService.evaluate",
        lambda self: report,
    )

    result = EsimIntegrationService("config/manifest.yaml").check_dependencies(
        esim_path=esim_root,
        dependency_paths={
            "ngspice": installed_tool,
            "kicad": tmp_path / "missing-kicad",
        },
    )

    assert result["esim"] == {
        "path": str(esim_root.resolve()),
        "detected": True,
        "path_valid": True,
    }
    assert result["dependencies"][0]["path_exists"] is True
    assert result["configured_dependency_paths"] == [
        {
            "dependency_id": "ngspice",
            "path": str(installed_tool.resolve()),
            "exists": True,
        },
        {
            "dependency_id": "kicad",
            "path": str((tmp_path / "missing-kicad").resolve()),
            "exists": False,
        },
    ]


def test_esim_report_rejects_invalid_explicit_root_and_unknown_dependency(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        "toolmate.integration.esim.detect_system_info",
        lambda: SystemInfo("Linux", "Test", "x86_64", (), False, None),
    )
    monkeypatch.setattr(
        "toolmate.integration.esim.ScanService.evaluate",
        lambda self: CompatibilityReport(entries=()),
    )
    service = EsimIntegrationService("config/manifest.yaml")

    with pytest.raises(FileNotFoundError):
        service.check_dependencies(esim_path=tmp_path / "missing")
    with pytest.raises(ValueError, match="Unknown dependency path ID"):
        service.check_dependencies(dependency_paths={"unknown": tmp_path})
