from src.toolmate.gui.main_window import MainWindow


def test_main_window_has_dashboard(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)

    assert window.windowTitle() == "ToolMate"
    assert window.centralWidget() is not None
