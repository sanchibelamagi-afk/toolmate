from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import (
    QFormLayout,
    QFrame,
    QGridLayout,
    QLabel,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from src.toolmate.core.models import CompatibilityReport, SystemInfo
from src.toolmate.gui.dependency_view import DependencyView
from src.toolmate.gui.log_viewer import LogViewer
from src.toolmate.gui.workers import ScanWorker


class Dashboard(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._thread: QThread | None = None
        self._worker: ScanWorker | None = None

        self.status_label = QLabel("Ready")
        self.scan_button = QPushButton("Scan / Refresh")
        self.scan_button.clicked.connect(self.refresh)

        self.system_form = QFormLayout()
        self.system_panel = QFrame()
        self.system_panel.setFrameShape(QFrame.StyledPanel)
        system_layout = QVBoxLayout(self.system_panel)
        system_layout.addWidget(QLabel("<b>System Information</b>"))
        system_layout.addLayout(self.system_form)

        self.summary_label = QLabel("No scan completed.")
        self.summary_label.setWordWrap(True)

        self.summary_panel = QFrame()
        self.summary_panel.setFrameShape(QFrame.StyledPanel)
        summary_layout = QVBoxLayout(self.summary_panel)
        summary_layout.addWidget(QLabel("<b>Environment Health</b>"))
        summary_layout.addWidget(self.summary_label)

        top = QGridLayout()
        top.addWidget(self.system_panel, 0, 0)
        top.addWidget(self.summary_panel, 0, 1)

        self.dependency_view = DependencyView()
        self.log_viewer = LogViewer()

        splitter = QSplitter()
        splitter.addWidget(self.dependency_view)
        splitter.addWidget(self.log_viewer)
        splitter.setSizes([650, 300])

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.scan_button)
        layout.addWidget(self.status_label)
        layout.addWidget(splitter)

    def refresh(self) -> None:
        if self._thread is not None and self._thread.isRunning():
            return

        self.status_label.setText("Scanning environment...")
        self.scan_button.setEnabled(False)

        self._thread = QThread(self)
        self._worker = ScanWorker()
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._apply_results)
        self._worker.failed.connect(self._show_failure)
        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()

    def _apply_results(self, info: SystemInfo, report: CompatibilityReport) -> None:
        self._set_system_info(info)
        self.dependency_view.set_report(report)
        counts = report.counts
        total = len(report.entries)
        installed = counts.get("installed", 0)
        problems = total - installed
        self.summary_label.setText(
            f"{total} dependencies checked\n"
            f"{installed} compatible\n"
            f"{problems} requiring attention"
        )
        self.status_label.setText("Scan complete")
        self.scan_button.setEnabled(True)
        self.log_viewer.refresh()

    def _show_failure(self, message: str) -> None:
        self.status_label.setText(f"Scan failed: {message}")
        self.scan_button.setEnabled(True)
        self.log_viewer.refresh()

    def _set_system_info(self, info: SystemInfo) -> None:
        while self.system_form.count():
            item = self.system_form.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.system_form.addRow("Operating system", QLabel(info.operating_system))
        self.system_form.addRow("OS version", QLabel(info.os_version))
        self.system_form.addRow("CPU architecture", QLabel(info.architecture))
        self.system_form.addRow(
            "Package manager",
            QLabel(", ".join(info.package_managers) if info.package_managers else "None detected"),
        )
        self.system_form.addRow(
            "Administrator",
            QLabel("Yes" if info.administrator else "No"),
        )
        self.system_form.addRow(
            "eSim location",
            QLabel(str(info.esim_path or "Not detected")),
        )
