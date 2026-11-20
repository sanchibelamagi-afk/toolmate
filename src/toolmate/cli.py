from pathlib import Path

from toolmate.diagnostics.logger import configure_logging
from toolmate.tui.app import ToolMateApp


def get_manifest_path() -> Path:
    project_root = Path(__file__).resolve().parents[2]
    manifest_path = project_root / "config" / "manifest.yaml"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"ToolMate manifest not found: {manifest_path}")
    return manifest_path


def main() -> int:
    configure_logging()
    manifest_path = get_manifest_path()
    ToolMateApp(str(manifest_path)).run()
    return 0
