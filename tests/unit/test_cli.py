from importlib.metadata import entry_points

from toolmate.cli import get_manifest_path


def test_console_script_points_to_cli_main():
    scripts = {entry.name: entry.value for entry in entry_points(group="console_scripts")}
    assert scripts["toolmate"] == "toolmate.cli:main"


def test_cli_resolves_manifest_from_installed_package():
    assert get_manifest_path().is_file()
