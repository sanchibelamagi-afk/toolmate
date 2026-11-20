from pathlib import Path

from toolmate.core.compatibility_checker import CompatibilityChecker
from toolmate.core.models import (
    DependencyInventoryEntry,
    DetectedInstallation,
)


MANIFEST = {
    "dependencies": [
        {
            "id": "python",
            "name": "Python",
            "version": {
                "minimum": "3.10",
                "maximum": None,
                "excluded": ["3.12.*"],
            },
        },
        {
            "id": "ngspice",
            "name": "Ngspice",
            "version": {},
        },
    ]
}


def test_compatible_version():
    inventory = [
        DependencyInventoryEntry(
            id="python",
            name="Python",
            status="installed",
            installations=(
                DetectedInstallation(
                    version="3.14.6",
                    path=None,
                    detection_method="executable",
                ),
            ),
        )
    ]
    report = CompatibilityChecker(MANIFEST).evaluate(inventory)
    assert report.entries[0].status == "installed"


def test_outdated_version():
    inventory = [
        DependencyInventoryEntry(
            id="python",
            name="Python",
            status="installed",
            installations=(
                DetectedInstallation(
                    version="3.9.1",
                    path=None,
                    detection_method="executable",
                ),
            ),
        )
    ]
    report = CompatibilityChecker(MANIFEST).evaluate(inventory)
    assert report.entries[0].status == "outdated"


def test_incompatible_excluded_version():
    inventory = [
        DependencyInventoryEntry(
            id="python",
            name="Python",
            status="installed",
            installations=(
                DetectedInstallation(
                    version="3.12.5",
                    path=None,
                    detection_method="executable",
                ),
            ),
        )
    ]
    report = CompatibilityChecker(MANIFEST).evaluate(inventory)
    assert report.entries[0].status == "incompatible"


def test_missing_dependency():
    inventory = [
        DependencyInventoryEntry(
            id="ngspice",
            name="Ngspice",
            status="missing",
            installations=(),
        )
    ]
    report = CompatibilityChecker(MANIFEST).evaluate(inventory)
    assert report.entries[0].status == "missing"


def test_unknown_version():
    inventory = [
        DependencyInventoryEntry(
            id="ngspice",
            name="Ngspice",
            status="unknown",
            installations=(
                DetectedInstallation(
                    version=None,
                    path=None,
                    detection_method="executable",
                ),
            ),
        )
    ]
    report = CompatibilityChecker(MANIFEST).evaluate(inventory)
    assert report.entries[0].status == "unknown"


def test_misconfigured_path():
    inventory = [
        DependencyInventoryEntry(
            id="ngspice",
            name="Ngspice",
            status="installed",
            installations=(
                DetectedInstallation(
                    version="44.0",
                    path=Path("/missing/ngspice"),
                    detection_method="known_path",
                ),
            ),
        )
    ]
    report = CompatibilityChecker(MANIFEST).evaluate(inventory)
    assert report.entries[0].status == "misconfigured"
