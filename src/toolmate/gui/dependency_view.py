from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.toolmate.core.models import CompatibilityReport, CompatibilityResult
from src.toolmate.gui.widgets.status_badge import StatusBadge


class DependencyView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Dependency", "Status", "Version", "Detail"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)

        self.detail = QLabel("Select a dependency to inspect it.")
        self.detail.setWordWrap(True)
        self.detail.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        layout = QVBoxLayout(self)
        layout.addWidget(self.table)
        layout.addWidget(self.detail)

        self.table.itemSelectionChanged.connect(self._show_selected_detail)
        self._entries: tuple[CompatibilityResult, ...] = ()

    def set_report(self, report: CompatibilityReport) -> None:
        self._entries = report.entries
        self.table.setRowCount(0)
        for row, entry in enumerate(report.entries):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(entry.name))

            badge = StatusBadge(entry.status)
            badge_widget = QWidget()
            badge_layout = QVBoxLayout(badge_widget)
            badge_layout.setContentsMargins(6, 3, 6, 3)
            badge_layout.addWidget(badge)
            badge_layout.setAlignment(Qt.AlignLeft)
            self.table.setCellWidget(row, 1, badge_widget)

            self.table.setItem(row, 2, QTableWidgetItem(entry.installed_version or "-"))
            self.table.setItem(row, 3, QTableWidgetItem(entry.detail))

        if report.entries:
            self.table.selectRow(0)

    def _show_selected_detail(self) -> None:
        selected = self.table.currentRow()
        if 0 <= selected < len(self._entries):
            entry = self._entries[selected]
            path = str(entry.path) if entry.path else "Not available"
            self.detail.setText(
                f"<b>{entry.name}</b><br>"
                f"Status: {entry.status}<br>"
                f"Version: {entry.installed_version or 'Unknown'}<br>"
                f"Path: {path}<br>"
                f"Detail: {entry.detail}"
            )
