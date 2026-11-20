from src.toolmate.core.manifest_manager import ManifestError, ManifestManager


def test_load_valid_manifest(tmp_path):
    manifest = tmp_path / "manifest.yaml"
    manifest.write_text(
        "manifest_version: 1\nesim_version: '2.x'\ndependencies: []\n",
        encoding="utf-8",
    )

    assert ManifestManager(manifest).load()["manifest_version"] == 1


def test_load_rejects_missing_manifest(tmp_path):
    try:
        ManifestManager(tmp_path / "missing.yaml").load()
    except ManifestError:
        return
    raise AssertionError("ManifestError was not raised")
