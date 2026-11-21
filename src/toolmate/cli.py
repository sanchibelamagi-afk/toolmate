import argparse
import json
from pathlib import Path
import sys

from toolmate.diagnostics.logger import configure_logging
from toolmate.integration.esim import EsimIntegrationService
from toolmate.tui.app import ToolMateApp


def get_manifest_path() -> Path:
    project_root = Path(__file__).resolve().parents[2]
    candidates = []
    bundle_root = getattr(sys, "_MEIPASS", None)
    if isinstance(bundle_root, str):
        candidates.append(Path(bundle_root) / "config" / "manifest.yaml")
    candidates.extend(
        (
            project_root / "config" / "manifest.yaml",
            Path(sys.prefix) / "share" / "toolmate" / "config" / "manifest.yaml",
        )
    )
    for manifest_path in candidates:
        if manifest_path.is_file():
            return manifest_path
    raise FileNotFoundError(
        "ToolMate manifest not found in the source tree or installed package data."
    )


def parse_dependency_paths(values: list[str]) -> dict[str, str]:
    dependency_paths: dict[str, str] = {}
    for value in values:
        dependency_id, separator, path = value.partition("=")
        if not separator or not dependency_id.strip() or not path.strip():
            raise ValueError(
                f"Invalid dependency path {value!r}; expected ID=PATH."
            )
        dependency_id = dependency_id.strip()
        if dependency_id in dependency_paths:
            raise ValueError(f"Dependency path specified more than once: {dependency_id}")
        dependency_paths[dependency_id] = path.strip()
    return dependency_paths


def main(argv: list[str] | None = None) -> int:
    logger = configure_logging()
    parser = argparse.ArgumentParser(description="eSim environment and dependency manager")
    parser.add_argument(
        "--check-dependencies",
        action="store_true",
        help="emit a JSON dependency report for eSim integration",
    )
    parser.add_argument(
        "--esim-path",
        type=Path,
        help="eSim installation directory to display or validate",
    )
    parser.add_argument(
        "--dependency-path",
        action="append",
        default=[],
        metavar="ID=PATH",
        help="validate an eSim-configured dependency path (repeatable)",
    )
    args = parser.parse_args(argv)

    if args.dependency_path and not args.check_dependencies:
        parser.error("--dependency-path requires --check-dependencies")

    manifest_path = get_manifest_path()
    if args.check_dependencies:
        try:
            dependency_paths = parse_dependency_paths(args.dependency_path)
            report = EsimIntegrationService(manifest_path).check_dependencies(
                esim_path=args.esim_path,
                dependency_paths=dependency_paths,
            )
        except (OSError, ValueError) as exc:
            logger.exception("eSim dependency check failed.")
            print(json.dumps({"schema_version": 1, "error": str(exc)}))
            return 2
        print(json.dumps(report, indent=2))
        return 0

    if args.esim_path is not None:
        try:
            args.esim_path = EsimIntegrationService._validated_directory(
                args.esim_path,
                "eSim",
            )
        except (OSError, ValueError) as exc:
            parser.error(str(exc))

    ToolMateApp(str(manifest_path), esim_path=args.esim_path).run()
    return 0
