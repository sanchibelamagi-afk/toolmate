from PyQt5.QtCore import QObject, pyqtSignal

from src.toolmate.core.system_detector import detect_system_info
from src.toolmate.services.scan_service import ScanService


class ScanWorker(QObject):
    finished = pyqtSignal(object, object)
    failed = pyqtSignal(str)

    def __init__(self, manifest_path: str = "config/manifest.yaml") -> None:
        super().__init__()
        self.manifest_path = manifest_path

    def run(self) -> None:
        try:
            info = detect_system_info()
            report = ScanService(self.manifest_path).evaluate()
            self.finished.emit(info, report)
        except Exception as exc:
            self.failed.emit(str(exc))
