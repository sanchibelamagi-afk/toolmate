from toolmate.services.install_service import InstallService


def test_manifest_has_verified_kicad_winget_id_and_ngspice_fallback():
    service = InstallService("config/manifest.yaml")
    kicad = service._dependency("kicad")
    ngspice = service._dependency("ngspice")

    assert kicad["package_manager"]["winget"] == "KiCad.KiCad"
    assert "winget" not in ngspice["package_manager"]
    assert ngspice["package_manager"]["choco"] == "ngspice"
    assert ngspice["installation"]["manual_url"] == "https://ngspice.sourceforge.io/download.html"


def test_install_requires_explicit_approval(tmp_path):
    manifest = tmp_path / "manifest.yaml"
    manifest.write_text(
        "manifest_version: 1\n"
        "dependencies:\n"
        "  - id: demo\n"
        "    name: Demo\n"
        "    detection:\n"
        "      method: executable\n"
        "      executable: demo\n",
        encoding="utf-8",
    )
    service = InstallService(str(manifest))

    try:
        service.execute("demo", approved=False)
    except PermissionError:
        return
    raise AssertionError("Installation was not blocked without approval")


def test_automatic_installability_uses_available_platform_package_manager(monkeypatch):
    service = InstallService("config/manifest.yaml")
    monkeypatch.setattr("toolmate.services.install_service.sys.platform", "win32")
    monkeypatch.setattr(
        "toolmate.services.install_service.shutil.which",
        lambda command: command == "choco",
    )

    assert service.can_install_automatically("ngspice")
    assert not service.can_install_automatically("python")
    assert service.plan("ngspice") == (
        ("choco", "install", "ngspice", "-y"),
        "Chocolatey package ngspice",
    )


def test_manifest_contains_full_esim_toolchain_and_package_mappings():
    service = InstallService("config/manifest.yaml")
    expected_ids = {
        "python",
        "ngspice",
        "kicad",
        "git",
        "ghdl",
        "openmodelica",
        "verilator",
        "iverilog",
        "makerchip",
        "openroad_flow",
        "skywater_sky130_pdk",
        "ihp_pdk",
    }

    assert {item["id"] for item in service.manifest["dependencies"]} == expected_ids
    assert service._dependency("git")["package_manager"] == {
        "winget": "Git.Git",
        "choco": "git",
        "apt": "git",
        "pacman": "git",
    }
    assert service._dependency("iverilog")["package_manager"] == {
        "winget": "Icarus.Verilog",
        "choco": "iverilog",
        "apt": "iverilog",
        "pacman": "iverilog",
    }
    assert service._dependency("ghdl")["package_manager"] == {
        "winget": "ghdl.ghdl.ucrt64.mcode",
        "apt": "ghdl",
    }
    assert service._dependency("openmodelica")["package_manager"] == {
        "winget": "OpenModelica.OpenModelica.Official",
        "apt": "openmodelica",
    }
    assert service._dependency("makerchip")["detection"]["method"] == "external"
    expected_version_commands = {
        "kicad": ("kicad-cli", ["version"]),
        "git": ("git", ["--version"]),
        "ngspice": ("ngspice", ["--version"]),
        "ghdl": ("ghdl", ["--version"]),
        "openmodelica": ("omc", ["--version"]),
        "verilator": ("verilator", ["--version"]),
        "iverilog": ("iverilog", ["-V"]),
    }
    for dependency_id, (executable, version_args) in expected_version_commands.items():
        detection = service._dependency(dependency_id)["detection"]
        assert detection["executable"] == executable
        assert detection["version_args"] == version_args
    assert service._dependency("openroad_flow")["detection"]["method"] == "path"
    assert service._dependency("skywater_sky130_pdk")["detection"]["method"] == "path"
    assert service._dependency("ihp_pdk")["detection"]["method"] == "path"


def test_plan_supports_pacman_for_linux_dependencies(monkeypatch):
    service = InstallService("config/manifest.yaml")
    monkeypatch.setattr("toolmate.services.install_service.sys.platform", "linux")
    monkeypatch.setattr(
        "toolmate.installers.pacman_installer._requires_sudo",
        lambda: True,
    )
    monkeypatch.setattr(
        "toolmate.services.install_service.shutil.which",
        lambda command: command == "pacman",
    )

    assert service.plan("verilator") == (
        ("sudo", "pacman", "-S", "--noconfirm", "--needed", "verilator"),
        "pacman package verilator",
    )
