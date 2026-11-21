import json
from pathlib import Path

import pytest

from toolmate.core.models import CompatibilityResult, SystemInfo
from toolmate.platform import windows
from toolmate.services.environment_service import EnvironmentConfigurationService


def _system_info(esim_path: Path | None) -> SystemInfo:
    return SystemInfo(
        operating_system="Linux",
        os_version="test",
        architecture="x86_64",
        package_managers=(),
        administrator=False,
        esim_path=esim_path,
    )


def test_profile_plan_and_apply_back_up_before_writing(monkeypatch, tmp_path):
    profile = tmp_path / ".profile"
    profile.write_text("# existing profile\n", encoding="utf-8")
    original_profile = profile.read_bytes()
    tool_directory = tmp_path / "tools"
    tool_directory.mkdir()
    executable = tool_directory / "git"
    executable.write_text("", encoding="utf-8")
    esim = tmp_path / "esim"
    (esim / "bin").mkdir(parents=True)
    monkeypatch.setattr(
        "toolmate.services.environment_service.linux.user_profile_path",
        lambda: profile,
    )
    service = EnvironmentConfigurationService(
        "config/manifest.yaml",
        backup_directory=tmp_path / "backups",
        platform_name="linux",
    )
    entries = (
        CompatibilityResult(
            id="git",
            name="Git",
            status="installed",
            installed_version="2.0",
            path=executable,
            detail="Detected.",
        ),
    )

    plan = service.plan(_system_info(esim), entries)
    assert plan.path_entries == (str(tool_directory.resolve()), str((esim / "bin").resolve()))
    assert "export ESIM_HOME=" in plan.preview()
    assert "export PATH=" in plan.preview()
    assert not list((tmp_path / "backups").glob("*"))
    with pytest.raises(PermissionError):
        service.apply(plan, approved=False)
    assert not profile.read_text(encoding="utf-8").count("ToolMate environment")

    backup = service.apply(plan, approved=True)
    assert backup.read_bytes() == original_profile
    contents = profile.read_text(encoding="utf-8")
    assert contents.count("# >>> ToolMate environment >>>") == 1
    assert contents.count("# <<< ToolMate environment <<<") == 1


def test_profile_plan_replaces_existing_managed_block(monkeypatch, tmp_path):
    profile = tmp_path / ".profile"
    profile.write_text(
        "before\n# >>> ToolMate environment >>>\nold\n"
        "# <<< ToolMate environment <<<\nafter\n",
        encoding="utf-8",
    )
    tool_directory = tmp_path / "tools"
    tool_directory.mkdir()
    executable = tool_directory / "git"
    executable.write_text("", encoding="utf-8")
    monkeypatch.setattr(
        "toolmate.services.environment_service.linux.user_profile_path",
        lambda: profile,
    )
    service = EnvironmentConfigurationService(
        "config/manifest.yaml",
        backup_directory=tmp_path / "backups",
        platform_name="linux",
    )
    entry = CompatibilityResult(
        id="git",
        name="Git",
        status="installed",
        installed_version="2.0",
        path=executable,
        detail="Detected.",
    )

    plan = service.plan(_system_info(None), (entry,))
    service.apply(plan, approved=True)
    contents = profile.read_text(encoding="utf-8")
    assert contents.startswith("before\n")
    assert contents.rstrip().endswith("after")
    assert contents.count("# >>> ToolMate environment >>>") == 1


def test_profile_change_after_preview_is_not_overwritten(monkeypatch, tmp_path):
    profile = tmp_path / ".profile"
    profile.write_text("before\n", encoding="utf-8")
    tool_directory = tmp_path / "tools"
    tool_directory.mkdir()
    executable = tool_directory / "git"
    executable.write_text("", encoding="utf-8")
    monkeypatch.setattr(
        "toolmate.services.environment_service.linux.user_profile_path",
        lambda: profile,
    )
    backup_directory = tmp_path / "backups"
    service = EnvironmentConfigurationService(
        "config/manifest.yaml",
        backup_directory=backup_directory,
        platform_name="linux",
    )
    entry = CompatibilityResult(
        id="git",
        name="Git",
        status="installed",
        installed_version="2.0",
        path=executable,
        detail="Detected.",
    )
    plan = service.plan(_system_info(None), (entry,))
    profile.write_text("changed by user\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="changed after preview"):
        service.apply(plan, approved=True)
    assert not list(backup_directory.glob("*"))
    assert profile.read_text(encoding="utf-8") == "changed by user\n"


def test_windows_user_environment_plan_and_backup(monkeypatch, tmp_path):
    tool_directory = tmp_path / "tools"
    tool_directory.mkdir()
    executable = tool_directory / "git.exe"
    executable.write_text("", encoding="utf-8")
    state = {"path": "C:\\Existing", "esim_home": None}
    writes = []
    monkeypatch.setattr(
        windows,
        "read_user_environment",
        lambda: (state["path"], state["esim_home"]),
    )
    monkeypatch.setattr(
        windows,
        "write_user_environment",
        lambda path, esim: writes.append((path, esim)),
    )
    service = EnvironmentConfigurationService(
        "config/manifest.yaml",
        backup_directory=tmp_path / "backups",
        platform_name="win32",
    )
    esim = tmp_path / "eSim"
    esim.mkdir()
    entry = CompatibilityResult(
        id="git",
        name="Git",
        status="installed",
        installed_version="2.0",
        path=executable,
        detail="Detected.",
    )

    plan = service.plan(_system_info(esim), (entry,))
    assert plan.target == r"HKCU\Environment"
    assert plan.path_value.startswith("C:\\Existing;")
    assert f"ESIM_HOME = {esim.resolve()}" in plan.preview()
    backup = service.apply(plan, approved=True)
    saved = json.loads(backup.read_text(encoding="utf-8"))
    assert saved["Path"] == "C:\\Existing"
    assert saved["ESIM_HOME"] is None
    assert writes == [(plan.path_value, str(esim.resolve()))]
