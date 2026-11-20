from toolmate.detection.package_manager_detector import detect_package_managers


def test_detector_returns_only_available_managers(monkeypatch):
    monkeypatch.setattr(
        "toolmate.detection.package_manager_detector.shutil.which",
        lambda name: "/usr/bin/apt" if name == "apt" else None,
    )

    assert detect_package_managers() == ("apt",)
