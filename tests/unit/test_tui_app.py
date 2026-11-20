import asyncio

from src.toolmate.tui.app import ToolMateApp


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
