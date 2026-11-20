import sys

from PyQt5.QtWidgets import (
    QApplication,
    QFormLayout,
    QLabel,
    QMainWindow,
    QWidget,
)

from src.toolmate.core.system_detector import detect_system_info


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("ToolMate")
        self.resize(720, 420)

        info = detect_system_info()
        layout = QFormLayout()
        layout.addRow("Operating system", QLabel(info.operating_system))
        layout.addRow("OS version", QLabel(info.os_version))
        layout.addRow("CPU architecture", QLabel(info.architecture))
        layout.addRow(
            "Package manager",
            QLabel(", ".join(info.package_managers) if info.package_managers else "None detected"),
        )
        layout.addRow("Administrator", QLabel("Yes" if info.administrator else "No"))
        layout.addRow("eSim location", QLabel(str(info.esim_path or "Not detected")))
        layout.addRow(
            "Environment variables",
            QLabel(
                "<br>".join(
                    f"{name}: {value}"
                    for name, value in sorted(info.environment_variables.items())
                )
                if info.environment_variables
                else "None detected"
            ),
        )

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec_()
