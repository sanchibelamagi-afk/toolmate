import sys

from PyQt5.QtWidgets import QApplication, QMainWindow

from src.toolmate.gui.dashboard import Dashboard


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("ToolMate")
        self.resize(980, 640)
        self.dashboard = Dashboard()
        self.setCentralWidget(self.dashboard)


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec_()
