from toolmate.detection.package_manager_detector import (
    detect_package_managers,
    query_package_version,
)


def test_detector_returns_only_available_managers(monkeypatch):
    monkeypatch.setattr(
        "toolmate.detection.package_manager_detector.shutil.which",
        lambda name: "/usr/bin/apt" if name == "apt" else None,
    )

    assert detect_package_managers() == ("apt",)


def test_pacman_queries_installed_package_version(monkeypatch):
    commands = []

    def run(command, **kwargs):
        commands.append(command)
        return type(
            "CompletedProcess",
            (),
            {
                "returncode": 0,
                "stdout": "Name : verilator\nVersion : 5.0.1-1\n",
                "stderr": "",
            },
        )()

    monkeypatch.setattr("toolmate.detection.package_manager_detector.subprocess.run", run)

    assert query_package_version("pacman", "verilator") == "5.0.1-1"
    assert commands == [["pacman", "-Qi", "verilator"]]
