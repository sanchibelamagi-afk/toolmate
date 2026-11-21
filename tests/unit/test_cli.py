import json
from importlib.metadata import entry_points
from pathlib import Path

import pytest

from toolmate import cli
from toolmate.cli import get_manifest_path


def test_console_script_points_to_cli_main():
    scripts = {entry.name: entry.value for entry in entry_points(group="console_scripts")}
    assert scripts["toolmate"] == "toolmate.cli:main"


def test_cli_resolves_manifest_from_installed_package():
    assert get_manifest_path().is_file()


def test_get_manifest_path_finds_packaged_data_file(monkeypatch, tmp_path):
    prefix = tmp_path / "venv"
    manifest_path = prefix / "share" / "toolmate" / "config" / "manifest.yaml"
    manifest_path.parent.mkdir(parents=True)
    manifest_path.write_text("manifest_version: 1\ndependencies: []\n", encoding="utf-8")
    monkeypatch.setattr(
        cli,
        "__file__",
        str(tmp_path / "site-packages" / "toolmate" / "cli.py"),
    )
    monkeypatch.setattr(cli.sys, "prefix", str(prefix))

    assert get_manifest_path() == manifest_path


def test_check_dependencies_command_emits_json(monkeypatch, capsys, tmp_path):
    esim_root = tmp_path / "esim"
    esim_root.mkdir()
    monkeypatch.setattr(cli, "get_manifest_path", lambda: Path("manifest.yaml"))
    monkeypatch.setattr(
        cli.EsimIntegrationService,
        "check_dependencies",
        lambda self, **kwargs: {"schema_version": 1, "esim_path": str(esim_root)},
    )

    assert cli.main(["--check-dependencies", "--esim-path", str(esim_root)]) == 0
    assert json.loads(capsys.readouterr().out) == {
        "schema_version": 1,
        "esim_path": str(esim_root),
    }


def test_dependency_path_arguments_require_unique_id_path_pairs():
    assert cli.parse_dependency_paths(
        ["ngspice=C:\\tools\\ngspice.exe", "kicad=/usr/bin/kicad-cli"]
    ) == {
        "ngspice": "C:\\tools\\ngspice.exe",
        "kicad": "/usr/bin/kicad-cli",
    }

    with pytest.raises(ValueError, match="expected ID=PATH"):
        cli.parse_dependency_paths(["ngspice"])
    with pytest.raises(ValueError, match="more than once"):
        cli.parse_dependency_paths(["ngspice=/one", "ngspice=/two"])
