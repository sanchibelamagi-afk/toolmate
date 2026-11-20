from pathlib import Path

from src.toolmate.core.dependency_scanner import DependencyScanner
from src.toolmate.core.manifest_manager import ManifestManager
from src.toolmate.core.models import DependencyInventoryEntry


class ScanService:
    def __init__(self, manifest_path: str | Path) -> None:
        self.manifest_path = Path(manifest_path)

    def scan(self) -> list[DependencyInventoryEntry]:
        manifest = ManifestManager(self.manifest_path).load()
        return DependencyScanner(manifest).scan()
