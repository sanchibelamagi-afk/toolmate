import json

import pytest

from toolmate.installers.base_installer import BaseInstaller
from toolmate.services.install_service import InstallService
from toolmate.services.update_service import UpdateService


@pytest.mark.parametrize(
    ("manager", "output", "packages", "expected"),
    [
        (
            "winget",
            "Name Id Version Available Source\nGit Git.Git 2.44 2.45 winget\n",
            {"Git.Git": "git"},
            {"git.git": "2.45"},
        ),
        (
            "apt",
            "Listing...\ngit/stable 2.45 amd64 [upgradable from: 2.44]\n",
            {"git": "git"},
            {"git": "2.45"},
        ),
        (
            "pacman",
            "git 2.44-1 -> 2.45-1\n",
            {"git": "git"},
            {"git": "2.45-1"},
        ),
        (
            "brew",
            json.dumps(
                {
                    "formulae": [
                        {"name": "git", "installed": ["2.44"], "current": "2.45"}
                    ],
                    "casks": [],
                }
            ),
            {"git": "git"},
            {"git": "2.45"},
        ),
    ],
)
def test_update_output_parsing(manager, output, packages, expected):
    assert UpdateService._parse_updates(manager, output, packages) == expected


def test_homebrew_update_check_and_plan(monkeypatch):
    service = UpdateService("config/manifest.yaml")
    commands = []
    monkeypatch.setattr("toolmate.services.update_service.sys.platform", "darwin")
    monkeypatch.setattr(
        "toolmate.services.update_service.shutil.which",
        lambda name: "/opt/homebrew/bin/brew" if name == "brew" else None,
    )

    def run(command, **kwargs):
        commands.append(command)
        return type(
            "CompletedProcess",
            (),
            {
                "returncode": 0,
                "stdout": json.dumps(
                    {
                        "formulae": [
                            {"name": "git", "installed": ["2.44"], "current": "2.45"}
                        ],
                        "casks": [],
                    }
                ),
                "stderr": "",
            },
        )()

    monkeypatch.setattr("toolmate.services.update_service.subprocess.run", run)

    assert service.check_available() == {"git": "2.45"}
    assert commands == [["brew", "outdated", "--json=v2"]]
    assert service.plan("git") == (
        ("brew", "upgrade", "git"),
        "brew package git",
    )


@pytest.mark.parametrize(
    ("platform", "manager", "output", "expected_command", "expected_version"),
    [
        (
            "win32",
            "winget",
            "Name Id Version Available Source\nGit Git.Git 2.44 2.45 winget\n",
            [
                "winget",
                "upgrade",
                "--accept-source-agreements",
                "--disable-interactivity",
            ],
            "2.45",
        ),
        (
            "linux",
            "apt",
            "Listing...\ngit/stable 2.45 amd64 [upgradable from: 2.44]\n",
            ["apt", "list", "--upgradable"],
            "2.45",
        ),
        (
            "linux",
            "pacman",
            "git 2.44-1 -> 2.45-1\n",
            ["pacman", "-Qu"],
            "2.45-1",
        ),
    ],
)
def test_available_update_checks_use_platform_package_manager(
    monkeypatch,
    platform,
    manager,
    output,
    expected_command,
    expected_version,
):
    service = UpdateService("config/manifest.yaml")
    commands = []
    monkeypatch.setattr("toolmate.services.update_service.sys.platform", platform)
    monkeypatch.setattr(
        "toolmate.services.update_service.shutil.which",
        lambda name: f"/usr/bin/{name}" if name == manager else None,
    )
    monkeypatch.setattr(
        "toolmate.services.update_service.subprocess.run",
        lambda command, **kwargs: (
            commands.append(command)
            or type(
                "CompletedProcess",
                (),
                {"returncode": 0, "stdout": output, "stderr": ""},
            )()
        ),
    )

    assert service.check_available() == {"git": expected_version}
    assert commands == [expected_command]


def test_update_check_reports_missing_package_manager(monkeypatch):
    service = UpdateService("config/manifest.yaml")
    monkeypatch.setattr("toolmate.services.update_service.sys.platform", "darwin")
    monkeypatch.setattr("toolmate.services.update_service.shutil.which", lambda name: None)

    with pytest.raises(RuntimeError, match="No supported update package manager"):
        service.check_available()


@pytest.mark.parametrize(
    ("platform", "manager", "expected_command", "expected_source"),
    [
        (
            "win32",
            "winget",
            (
                "winget",
                "upgrade",
                "--id",
                "Git.Git",
                "--exact",
                "--accept-package-agreements",
                "--accept-source-agreements",
                "--disable-interactivity",
            ),
            "winget package Git.Git",
        ),
        (
            "linux",
            "apt",
            ("apt-get", "install", "--only-upgrade", "-y", "git"),
            "apt package git",
        ),
        (
            "linux",
            "pacman",
            ("pacman", "-S", "--noconfirm", "--needed", "git"),
            "pacman package git",
        ),
    ],
)
def test_update_plans_use_supported_platform_commands(
    monkeypatch,
    platform,
    manager,
    expected_command,
    expected_source,
):
    service = UpdateService("config/manifest.yaml")
    monkeypatch.setattr("toolmate.services.update_service.sys.platform", platform)
    monkeypatch.setattr(
        "toolmate.services.update_service.shutil.which",
        lambda name: f"/usr/bin/{name}" if name == manager else None,
    )
    monkeypatch.setattr(
        "toolmate.installers.apt_installer._requires_sudo",
        lambda: False,
    )
    monkeypatch.setattr(
        "toolmate.installers.pacman_installer._requires_sudo",
        lambda: False,
    )

    assert service.plan("git") == (expected_command, expected_source)


def test_update_requires_approval_before_executing(monkeypatch):
    service = UpdateService("config/manifest.yaml")
    monkeypatch.setattr("toolmate.services.update_service.sys.platform", "darwin")
    monkeypatch.setattr(
        "toolmate.services.update_service.shutil.which",
        lambda name: "/opt/homebrew/bin/brew" if name == "brew" else None,
    )
    monkeypatch.setattr(
        BaseInstaller,
        "execute",
        lambda *args, **kwargs: pytest.fail("unapproved update was executed"),
    )

    with pytest.raises(PermissionError, match="explicit user approval"):
        service.execute("git", approved=False)


def test_homebrew_install_plan(monkeypatch):
    service = InstallService("config/manifest.yaml")
    monkeypatch.setattr("toolmate.services.install_service.sys.platform", "darwin")
    monkeypatch.setattr(
        "toolmate.services.install_service.shutil.which",
        lambda name: "/opt/homebrew/bin/brew" if name == "brew" else None,
    )

    assert service.plan("git") == (("brew", "install", "git"), "Homebrew package git")
    assert service.can_install_automatically("git")
