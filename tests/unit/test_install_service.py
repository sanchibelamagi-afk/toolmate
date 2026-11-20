from src.toolmate.services.install_service import InstallService


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
