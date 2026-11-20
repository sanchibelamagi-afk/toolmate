from src.toolmate.detection.executable_detector import detect_executables


def test_detect_executable_unknown_version(monkeypatch, tmp_path):
    executable = tmp_path / "tool.exe"
    executable.write_text("", encoding="utf-8")
    monkeypatch.setattr(
        "src.toolmate.detection.executable_detector.shutil.which",
        lambda name: str(executable),
    )
    monkeypatch.setattr(
        "src.toolmate.detection.executable_detector.subprocess.run",
        lambda *args, **kwargs: type(
            "Result",
            (),
            {"stdout": "tool version unknown", "stderr": "", "returncode": 0},
        )(),
    )

    detections = detect_executables("tool")

    assert len(detections) == 1
    assert detections[0].path is not None
    assert detections[0].version is None
