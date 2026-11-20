from importlib import metadata

from src.toolmate.core.models import DetectedInstallation


def detect_python_package(package_name: str) -> list[DetectedInstallation]:
    try:
        distribution = metadata.distribution(package_name)
        path = distribution.locate_file("")
        version = distribution.version
    except metadata.PackageNotFoundError:
        return []
    except (OSError, metadata.MetadataError) as exc:
        raise RuntimeError(f"Unable to inspect Python package {package_name}: {exc}") from exc

    return [
        DetectedInstallation(
            version=version,
            path=path,
            detection_method="python_package",
        )
    ]
