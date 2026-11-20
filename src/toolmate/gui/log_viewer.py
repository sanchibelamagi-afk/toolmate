from pathlib import Path

from PyQt5.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget


class LogViewer(QWidget):
    def __init__(self, log_path: str = "logs/toolmate.log") -> None:
        super().__init__()
        self.log_path = Path(log_path)
        self.title = QLabel("Logs")
        self.output = QTextEdit()
        self.output.setReadOnly(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.title)
        layout.addWidget(self.output)
        self.refresh()

    def refresh(self) -> None:
        if not self.log_path.exists():
            self.output.setPlainText("No log entries yet.")
            return
        try:
            text = self.log_path.read_text(encoding="utf-8")
        except OSError as exc:
            text = f"Unable to read log: {exc}"
        self.output.setPlainText(text[-12000:])
