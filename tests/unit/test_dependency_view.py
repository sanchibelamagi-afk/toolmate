from src.toolmate.core.models import CompatibilityReport, CompatibilityResult
from src.toolmate.gui.dependency_view import DependencyView


def test_dependency_view_populates_report_and_detail(qtbot):
    view = DependencyView()
    qtbot.addWidget(view)
    report = CompatibilityReport(
        entries=(
            CompatibilityResult(
                id="python",
                name="Python",
                status="installed",
                installed_version="3.14",
                path=None,
                detail="Compatible.",
            ),
            CompatibilityResult(
                id="ngspice",
                name="Ngspice",
                status="missing",
                installed_version=None,
                path=None,
                detail="Not detected.",
            ),
        )
    )

    view.set_report(report)

    assert view.table.rowCount() == 2
    assert view.table.item(0, 0).text() == "Python"
    assert "Python" in view.detail.text()
