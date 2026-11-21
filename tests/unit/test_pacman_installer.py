from toolmate.installers.base_installer import InstallationResult
from toolmate.installers.pacman_installer import PacmanInstaller


def test_pacman_installer_uses_sudo_and_noninteractive_install(monkeypatch):
    commands = []
    monkeypatch.setattr(
        "toolmate.installers.pacman_installer._requires_sudo",
        lambda: True,
    )

    def execute(self, command, on_output=None, cancel_event=None):
        commands.append(command)
        return InstallationResult(tuple(command), 0, "")

    monkeypatch.setattr(PacmanInstaller, "execute", execute)

    result = PacmanInstaller().install("iverilog")

    assert commands == [["sudo", "pacman", "-S", "--noconfirm", "--needed", "iverilog"]]
    assert result.succeeded
