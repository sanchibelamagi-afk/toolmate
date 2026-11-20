from pathlib import Path
from typing import Any

import yaml


class ManifestError(ValueError):
    pass


class ManifestManager:
    def __init__(self, manifest_path: str | Path) -> None:
        self.manifest_path = Path(manifest_path)

    def load(self) -> dict[str, Any]:
        if not self.manifest_path.exists():
            raise ManifestError(f"Manifest not found: {self.manifest_path}")

        try:
            with self.manifest_path.open("r", encoding="utf-8") as manifest_file:
                manifest = yaml.safe_load(manifest_file)
        except yaml.YAMLError as exc:
            raise ManifestError(f"Invalid manifest YAML: {exc}") from exc

        if not isinstance(manifest, dict):
            raise ManifestError("Manifest root must be a mapping")
        if manifest.get("manifest_version") is None:
            raise ManifestError("Manifest is missing manifest_version")
        if not isinstance(manifest.get("dependencies"), list):
            raise ManifestError("Manifest must contain a dependencies list")
        return manifest
