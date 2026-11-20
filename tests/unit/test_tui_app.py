import asyncio

from src.toolmate.core.models import CompatibilityReport, CompatibilityResult
from src.toolmate.tui.app import InstallConfirmScreen, ToolMateApp


def test_textual_app_smoke(monkeypatch):
    monkeypatch.setattr(
        "src.toolmate.tui.app.detect_system_info",
        lambda: type(
            "SystemInfo",
            (),
            {
                "operating_system": "Linux",
                "os_version": "Test OS",
                "architecture": "x86_64",
                "package_managers": ("apt",),
                "administrator": False,
                "esim_path": None,
            },
        )(),
    )
    monkeypatch.setattr(
        "src.toolmate.tui.app.ScanService.evaluate",
        lambda self: type(
            "Report",
            (),
            {"entries": (), "counts": {}},
        )(),
    )

    async def smoke():
        app = ToolMateApp()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            assert app.query_one("#header-bar") is not None
            assert app.query_one("#dependency-table") is not None
            assert app.query_one("#detail") is not None
            assert app.query_one("#install-output") is not None

    asyncio.run(smoke())


def test_install_action_opens_confirmation_modal(monkeypatch):
    monkeypatch.setattr(
        "src.toolmate.tui.app.detect_system_info",
        lambda: type(
            "SystemInfo",
            (),
            {
                "operating_system": "Linux",
                "os_version": "Test OS",
                "architecture": "x86_64",
                "package_managers": ("apt",),
                "administrator": False,
                "esim_path": None,
            },
        )(),
    )
    monkeypatch.setattr(
        "src.toolmate.tui.app.ScanService.evaluate",
        lambda self: CompatibilityReport(
            entries=(
                CompatibilityResult(
                    id="demo",
                    name="Demo",
                    status="missing",
                    installed_version=None,
                    path=None,
                    detail="Not detected.",
                ),
            )
        ),
    )
    monkeypatch.setattr(
        "src.toolmate.tui.app.ToolMateApp._planned_command",
        lambda self, entry: "apt-get install -y demo",
    )

    async def smoke():
        app = ToolMateApp()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            app.selected_id = "demo"
            app.action_install()
            await pilot.pause()

            assert isinstance(app.screen, InstallConfirmScreen)
            assert app.screen.dependency_name == "Demo"

            app.screen.dismiss(False)
            await pilot.pause()
            assert not isinstance(app.screen, InstallConfirmScreen)

    asyncio.run(smoke())
