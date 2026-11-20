from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel


STATUS_COLORS = {
    "installed": "#2e7d32",
    "missing": "#c62828",
    "outdated": "#ef6c00",
    "incompatible": "#c62828",
    "misconfigured": "#ad1457",
    "unknown": "#616161",
    "failed": "#b71c1c",
}


class StatusBadge(QLabel):
    def __init__(self, status: str = "unknown") -> None:
        super().__init__()
        self.set_status(status)

    def set_status(self, status: str) -> None:
        color = STATUS_COLORS.get(status, "#616161")
        self.setText(status.upper())
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(
            "QLabel {"
            f" background-color: {color};"
            " color: white;"
            " border-radius: 4px;"
            " padding: 4px 8px;"
            " font-weight: bold;"
            " }"
        )
