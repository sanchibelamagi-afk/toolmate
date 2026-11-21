from dataclasses import replace
from pathlib import Path
from typing import Any, Mapping

from toolmate.core.system_detector import detect_system_info
from toolmate.services.scan_service import ScanService


class EsimIntegrationService:
    def __init__(self, manifest_path: str | Path) -> None:
        self.manifest_path = Path(manifest_path)

    def check_dependencies(
        self,
        esim_path: str | Path | None = None,
        dependency_paths: Mapping[str, str | Path] | None = None,
    ) -> dict[str, Any]:
        system_info = detect_system_info()
        resolved_esim_path = system_info.esim_path
        if esim_path is not None:
            resolved_esim_path = self._validated_directory(esim_path, "eSim")
            system_info = replace(system_info, esim_path=resolved_esim_path)

        report = ScanService(self.manifest_path).evaluate()
        dependency_ids = {entry.id for entry in report.entries}
        configured_paths = []
        for dependency_id, value in (dependency_paths or {}).items():
            if dependency_id not in dependency_ids:
                raise ValueError(f"Unknown dependency path ID: {dependency_id}")
            path = Path(value).expanduser().resolve()
            configured_paths.append(
                {
                    "dependency_id": dependency_id,
                    "path": str(path),
                    "exists": path.exists(),
                }
            )

        dependencies = []
        for entry in report.entries:
            path = entry.path
            dependencies.append(
                {
                    "id": entry.id,
                    "name": entry.name,
                    "status": entry.status,
                    "version": entry.installed_version,
                    "path": str(path) if path else None,
                    "path_exists": path.exists() if path else None,
                    "detail": entry.detail,
                }
            )

        return {
            "schema_version": 1,
            "system": {
                "operating_system": system_info.operating_system,
                "os_version": system_info.os_version,
                "architecture": system_info.architecture,
            },
            "esim": {
                "path": str(resolved_esim_path) if resolved_esim_path else None,
                "detected": resolved_esim_path is not None,
                "path_valid": (
                    resolved_esim_path.is_dir()
                    if resolved_esim_path is not None
                    else False
                ),
            },
            "dependency_counts": dict(report.counts),
            "dependencies": dependencies,
            "configured_dependency_paths": configured_paths,
        }

    @staticmethod
    def _validated_directory(value: str | Path, label: str) -> Path:
        path = Path(value).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"{label} directory does not exist: {path}")
        if not path.is_dir():
            raise NotADirectoryError(f"{label} path is not a directory: {path}")
        return path
