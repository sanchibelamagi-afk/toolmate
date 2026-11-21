import asyncio
import logging

from toolmate.core.models import CompatibilityReport, CompatibilityResult
from toolmate.installers.base_installer import InstallationResult
from toolmate.tui.app import (
    InstallAllConfirmScreen,
    InstallConfirmScreen,
    SafeModePreviewScreen,
    ToolMateApp,
)


def test_textual_app_smoke(monkeypatch):
    monkeypatch.setattr(
        "toolmate.tui.app.detect_system_info",
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
        "toolmate.tui.app.ScanService.evaluate",
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
            assert app.query_one("#header-bar").border_title == "System Overview"
            assert app.query_one("#list-pane").border_title == "Dependencies"
            assert app.query_one("#detail-pane").border_title == "Package Details"
            assert app.query_one("#install-output").border_title == "Install Output"
            assert app.query_one("#status-strip").border_title == "Environment Health"

    asyncio.run(smoke())


def test_install_action_opens_confirmation_modal(monkeypatch):
    monkeypatch.setattr(
        "toolmate.tui.app.detect_system_info",
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
        "toolmate.tui.app.ScanService.evaluate",
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
        "toolmate.tui.app.ToolMateApp._planned_command",
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


def test_install_all_missing_shortcut_shows_eligible_missing_commands(monkeypatch):
    entries = (
        CompatibilityResult(
            id="auto",
            name="Automated Tool",
            status="missing",
            installed_version=None,
            path=None,
            detail="Not detected.",
        ),
        CompatibilityResult(
            id="manual",
            name="Manual Tool",
            status="missing",
            installed_version=None,
            path=None,
            detail="Not detected.",
        ),
        CompatibilityResult(
            id="installed",
            name="Installed Tool",
            status="installed",
            installed_version="1.0",
            path=None,
            detail="Available.",
        ),
    )
    monkeypatch.setattr(
        "toolmate.tui.app.detect_system_info",
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
        "toolmate.tui.app.ScanService.evaluate",
        lambda self: CompatibilityReport(entries=entries),
    )
    monkeypatch.setattr(
        "toolmate.tui.app.InstallService.can_install_automatically",
        lambda self, dependency_id: dependency_id == "auto",
    )
    monkeypatch.setattr(
        "toolmate.tui.app.ToolMateApp._planned_command",
        lambda self, entry: "apt-get install -y automated-tool",
    )

    async def smoke():
        app = ToolMateApp()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            assert app.focused is app.query_one("#dependency-table")
            await pilot.press("b")
            await pilot.pause()

            assert isinstance(app.screen, InstallAllConfirmScreen)
            assert [entry.id for entry, _ in app.screen.items] == ["auto"]
            assert app.screen.items[0][1] == "apt-get install -y automated-tool"
            app.screen.dismiss(False)

    asyncio.run(smoke())


def test_batch_installation_continues_after_an_item_fails(monkeypatch, caplog):
    entries = (
        CompatibilityResult(
            id="fails",
            name="First Tool",
            status="missing",
            installed_version=None,
            path=None,
            detail="Not detected.",
        ),
        CompatibilityResult(
            id="succeeds",
            name="Second Tool",
            status="missing",
            installed_version=None,
            path=None,
            detail="Not detected.",
        ),
    )
    monkeypatch.setattr(
        "toolmate.tui.app.detect_system_info",
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
        "toolmate.tui.app.ScanService.evaluate",
        lambda self: CompatibilityReport(entries=entries),
    )
    monkeypatch.setattr(
        "toolmate.tui.app.ToolMateApp._planned_command",
        lambda self, entry: f"apt-get install -y {entry.id}",
    )
    executed = []

    def execute(self, dependency_id, approved, on_output=None, cancel_event=None):
        executed.append((dependency_id, approved))
        if dependency_id == "fails":
            raise RuntimeError("package manager failed")
        if on_output is not None:
            on_output("installer output")
        return InstallationResult(
            command=("apt-get", "install", dependency_id),
            exit_code=0,
            output="",
        )

    monkeypatch.setattr("toolmate.tui.app.InstallService.execute", execute)

    async def smoke():
        app = ToolMateApp()
        async with app.run_test(size=(120, 40)):
            await app._run_batch_installations(entries)
            assert executed == [("fails", True), ("succeeds", True)]
            assert not app.install_in_progress
            assert app.active_install_cancel is None

    with caplog.at_level(logging.INFO, logger="toolmate"):
        asyncio.run(smoke())

    assert "Environment scan completed" in caplog.text
    assert "Batch installer output: installer output" in caplog.text
    assert "Batch installation failed for fails" in caplog.text


def test_safe_mode_toggle_updates_header_and_footer(monkeypatch):
    monkeypatch.setattr(
        "toolmate.tui.app.detect_system_info",
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
        "toolmate.tui.app.ScanService.evaluate",
        lambda self: CompatibilityReport(entries=()),
    )

    async def smoke():
        app = ToolMateApp()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            assert not app.safe_mode
            app.install_in_progress = True
            await pilot.press("m")
            await pilot.pause()
            assert not app.safe_mode

            app.install_in_progress = False
            await pilot.press("m")
            await pilot.pause()

            assert app.safe_mode
            assert "SAFE MODE: ON" in str(
                app.query_one("#header-bar").renderable
            )
            assert "Safe Mode: ON" in str(app.query_one("#keys").renderable)

    asyncio.run(smoke())


def test_safe_mode_previews_single_and_batch_without_execution(monkeypatch, caplog):
    entries = (
        CompatibilityResult(
            id="git",
            name="Git",
            status="missing",
            installed_version=None,
            path=None,
            detail="Not detected.",
        ),
        CompatibilityResult(
            id="ghdl",
            name="GHDL",
            status="missing",
            installed_version=None,
            path=None,
            detail="Not detected.",
        ),
    )
    monkeypatch.setattr(
        "toolmate.tui.app.detect_system_info",
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
        "toolmate.tui.app.ScanService.evaluate",
        lambda self: CompatibilityReport(entries=entries),
    )
    monkeypatch.setattr(
        "toolmate.tui.app.InstallService.can_install_automatically",
        lambda self, dependency_id: True,
    )
    monkeypatch.setattr(
        "toolmate.tui.app.ToolMateApp._planned_command",
        lambda self, entry: f"install {entry.id}",
    )
    monkeypatch.setattr(
        "toolmate.tui.app.InstallService.execute",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("Safe Mode must not execute installation commands")
        ),
    )

    async def smoke():
        app = ToolMateApp()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            app.selected_id = "git"
            await pilot.press("m")
            await pilot.press("i")
            await pilot.pause()

            assert isinstance(app.screen, SafeModePreviewScreen)
            assert app.screen.items == (("Git", "install git"),)
            assert not app.install_in_progress
            app.screen.dismiss(None)
            await pilot.pause()

            await pilot.press("b")
            await pilot.pause()
            assert isinstance(app.screen, SafeModePreviewScreen)
            assert app.screen.items == (
                ("Git", "install git"),
                ("GHDL", "install ghdl"),
            )
            assert not app.install_in_progress

    with caplog.at_level(logging.INFO, logger="toolmate"):
        asyncio.run(smoke())

    assert "Safe Mode install preview for git: install git" in caplog.text
    assert "Safe Mode batch install command preview for ghdl: install ghdl" in caplog.text
