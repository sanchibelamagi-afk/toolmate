from src.toolmate.gui.widgets.status_badge import STATUS_COLORS, StatusBadge


def test_status_badge_displays_status(qtbot):
    badge = StatusBadge("outdated")
    qtbot.addWidget(badge)

    assert badge.text() == "OUTDATED"
    assert STATUS_COLORS["outdated"] in badge.styleSheet()


def test_status_badge_updates_status(qtbot):
    badge = StatusBadge("missing")
    qtbot.addWidget(badge)
    badge.set_status("installed")

    assert badge.text() == "INSTALLED"
