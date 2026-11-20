from src.toolmate.services.install_service import InstallService


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
