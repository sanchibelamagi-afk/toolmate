import asyncio
from dataclasses import replace
from pathlib import Path
from threading import Event

import psutil
from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    RichLog,
    Static,
)

from toolmate.core.models import CompatibilityReport, CompatibilityResult, SystemInfo
from toolmate.core.system_detector import detect_system_info
from toolmate.diagnostics.logger import configure_logging
from toolmate.services.environment_service import (
    EnvironmentConfigurationService,
    EnvironmentPlan,
)
from toolmate.services.scan_service import ScanService
from toolmate.services.install_service import InstallService
from toolmate.services.update_service import UpdateService


STATUS_COLORS = {
    "installed": "green",
    "missing": "red",
    "outdated": "yellow",
    "incompatible": "red",
    "misconfigured": "magenta",
    "unknown": "grey62",
    "unsupported": "grey50",
    "failed": "red",
}


class InstallConfirmScreen(ModalScreen[bool]):
    def __init__(self, name: str, command: str) -> None:
        super().__init__()
        self.dependency_name = name
        self.command = command

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-dialog"):
            yield Static(f"[bold]Install {self.dependency_name}[/bold]")
            yield Static(Text(self.command, style="bold cyan"), id="confirm-command")
            yield Static("No command will execute automatically.")
            with Horizontal(id="confirm-actions"):
                yield Button("Cancel", id="cancel")
                yield Button("Confirm", id="confirm", variant="success")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "confirm")


class UpdateConfirmScreen(ModalScreen[bool]):
    def __init__(self, name: str, command: str) -> None:
        super().__init__()
        self.dependency_name = name
        self.command = command

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-dialog"):
            yield Static(f"[bold]Update {self.dependency_name}[/bold]")
            yield Static(Text(self.command, style="bold cyan"), id="confirm-command")
            yield Static("No command will execute automatically.")
            with Horizontal(id="confirm-actions"):
                yield Button("Cancel", id="cancel")
                yield Button("Confirm", id="confirm", variant="success")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "confirm")


class EnvironmentConfirmScreen(ModalScreen[bool]):
    def __init__(self, plan: EnvironmentPlan) -> None:
        super().__init__()
        self.plan = plan

    def compose(self) -> ComposeResult:
        with Vertical(id="environment-confirm-dialog"):
            yield Static("[bold]Configure user environment[/bold]")
            yield Static(
                "A backup will be created before the profile or User PATH is modified."
            )
            with VerticalScroll(id="environment-plan"):
                yield Static(Text(self.plan.preview(), style="cyan"))
            with Horizontal(id="confirm-actions"):
                yield Button("Cancel", id="cancel")
                yield Button("Confirm", id="confirm", variant="success")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "confirm")


class InstallAllConfirmScreen(ModalScreen[bool]):
    def __init__(
        self,
        items: tuple[tuple[CompatibilityResult, str], ...],
    ) -> None:
        super().__init__()
        self.items = items

    def compose(self) -> ComposeResult:
        with Vertical(id="batch-confirm-dialog"):
            yield Static(
                f"[bold]Install {len(self.items)} missing dependencies?[/bold]"
            )
            yield Static(
                "Only dependencies with supported automated package managers are included."
            )
            yield Static("Review the planned commands before approving the batch.")
            with VerticalScroll(id="batch-plan"):
                for entry, command in self.items:
                    yield Static(f"[bold]{entry.name}[/bold]\n{command}")
            with Horizontal(id="confirm-actions"):
                yield Button("Cancel", id="cancel")
                yield Button("Confirm", id="confirm", variant="success")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "confirm")


class SafeModePreviewScreen(ModalScreen[None]):
    def __init__(
        self,
        title: str,
        items: tuple[tuple[str, str], ...],
    ) -> None:
        super().__init__()
        self.preview_title = title
        self.items = items

    def compose(self) -> ComposeResult:
        with Vertical(id="preview-dialog"):
            yield Static(f"[bold]{self.preview_title}[/bold]")
            yield Static("Safe Mode is ON. No system changes will be made.")
            with VerticalScroll(id="preview-commands"):
                for name, command in self.items:
                    yield Static(f"[bold]{name}[/bold]\n{command}")
            with Horizontal(id="confirm-actions"):
                yield Button("Close", id="close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(None)


class ToolMateApp(App[None]):
    TITLE = "ToolMate"
    SUB_TITLE = "eSim Dependency Manager"

    CSS = """
    Screen {
        background: #1a1b26;
        color: #c0caf5;
    }
    #header-bar {
        height: 4;
        padding: 0 2;
        border: round #414868;
        background: #24283b;
        border-title-color: #7aa2f7;
        border-title-style: bold;
    }
    #status-strip {
        height: 3;
        content-align: center middle;
        border: round #414868;
        background: #1f2335;
        border-title-color: #bb9af7;
        border-title-style: bold;
    }
    #workspace {
        height: 1fr;
        margin: 0 1;
    }
    #list-pane {
        width: 2fr;
        border: round #414868;
        padding: 0 1;
        border-title-color: #7aa2f7;
        border-title-style: bold;
    }
    #detail-pane {
        width: 1fr;
        border: round #414868;
        padding: 1 2;
        border-title-color: #bb9af7;
        border-title-style: bold;
    }
    #search {
        margin: 1 0;
    }
    #dependency-table {
        height: 1fr;
    }
    #detail {
        height: 1fr;
    }
    #install-output {
        height: 10;
        border: round #414868;
        border-title-color: #7dcfff;
        border-title-style: bold;
    }
    #keys {
        height: 3;
        content-align: center middle;
        background: #24283b;
        color: #c0caf5;
        border-top: solid #414868;
    }
    #confirm-dialog {
        width: 78;
        height: 12;
        margin: 2 4;
        padding: 1 2;
        border: thick #7aa2f7;
        background: #24283b;
    }
    #environment-confirm-dialog {
        width: 90;
        height: 28;
        margin: 1 4;
        padding: 1 2;
        border: thick #7aa2f7;
        background: #24283b;
    }
    #environment-plan {
        height: 1fr;
        margin: 1 0;
        padding: 0 1;
        border: round #414868;
        background: #1a1b26;
    }
    #confirm-command {
        height: 3;
        margin: 1 0;
        padding: 1;
        background: #1a1b26;
    }
    #confirm-actions {
        height: 3;
        align-horizontal: right;
    }
    #batch-confirm-dialog {
        width: 90;
        height: 24;
        margin: 2 4;
        padding: 1 2;
        border: thick #7aa2f7;
        background: #24283b;
    }
    #batch-plan {
        height: 1fr;
        margin: 1 0;
        padding: 0 1;
        border: round #414868;
        background: #1a1b26;
    }
    #preview-dialog {
        width: 90;
        height: 24;
        margin: 2 4;
        padding: 1 2;
        border: thick #e0af68;
        background: #24283b;
    }
    #preview-commands {
        height: 1fr;
        margin: 1 0;
        padding: 0 1;
        border: round #414868;
        background: #1a1b26;
    }
    """

    BINDINGS = [
        Binding("s", "scan", "[s] Scan"),
        Binding("i", "install", "[i] Install"),
        Binding("u", "update", "[u] Update"),
        Binding("b", "install_all_missing", "[b] Install All Missing"),
        Binding("c", "configure_environment", "[c] Configure Env"),
        Binding("m", "toggle_safe_mode", "[m] Safe Mode"),
        Binding("x", "cancel_install", "[x] Cancel operation"),
        Binding("slash", "filter", "[/] Filter"),
        Binding("q", "quit", "[q] Quit"),
    ]

    def __init__(
        self,
        manifest_path: str = "config/manifest.yaml",
        esim_path: Path | None = None,
    ) -> None:
        super().__init__()
        self.manifest_path = manifest_path
        self.esim_path = esim_path
        self.logger = configure_logging()
        self.report: CompatibilityReport | None = None
        self.entries = []
        self.selected_id: str | None = None
        self.active_install_cancel: Event | None = None
        self.install_in_progress = False
        self.safe_mode = False
        self.system_info: SystemInfo | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Detecting system...", id="header-bar")
        yield Static("No scan completed.", id="status-strip")
        with Horizontal(id="workspace"):
            with Vertical(id="list-pane"):
                yield Input(placeholder="Filter dependencies...", id="search")
                table = DataTable(id="dependency-table")
                table.add_columns("Dependency", "Status", "Version")
                table.cursor_type = "row"
                table.zebra_stripes = True
                yield table
            with Vertical(id="detail-pane"):
                yield Static("Select a dependency.", id="detail")
                yield RichLog(id="install-output", wrap=True, highlight=True)
        yield Static(
            "s Scan   i Install   u Update   b Install All Missing   "
            "c Configure Env   m Safe Mode: OFF   "
            "x Cancel operation   / Filter   q Quit",
            id="keys",
        )
        yield Footer()

    async def on_mount(self) -> None:
        self.query_one("#header-bar", Static).border_title = "System Overview"
        self.query_one("#status-strip", Static).border_title = "Environment Health"
        self.query_one("#list-pane", Vertical).border_title = "Dependencies"
        self.query_one("#detail-pane", Vertical).border_title = "Package Details"
        self.query_one("#install-output", RichLog).border_title = "Install Output"
        self.query_one("#dependency-table", DataTable).focus()
        await self.action_scan()

    async def action_scan(self) -> None:
        self.notify("Scanning system and dependencies...")
        self.logger.info("Starting environment scan.")
        try:
            info, report = await asyncio.to_thread(self._scan)
        except Exception as exc:
            self.logger.exception("Environment scan failed.")
            self.notify(f"Scan failed: {exc}", severity="error")
            return
        self.report = report
        self.entries = list(report.entries)
        self._render_header(info)
        self._render_table(self.entries)
        self.logger.info(
            "Environment scan completed: total=%d status_counts=%s",
            len(report.entries),
            dict(report.counts),
        )
        self.notify("Scan complete")

    def _scan(self) -> tuple[SystemInfo, CompatibilityReport]:
        info = detect_system_info()
        if self.esim_path is not None:
            info = replace(info, esim_path=self.esim_path)
        report = ScanService(self.manifest_path).evaluate()
        return info, report

    def _main_screen(self) -> Screen[None]:
        return self.screen_stack[0]

    def _render_header(self, info: SystemInfo) -> None:
        self.system_info = info
        managers = ", ".join(info.package_managers) if info.package_managers else "None"
        cpu_count = psutil.cpu_count(logical=True) or "Unknown"
        memory_gib = psutil.virtual_memory().total / (1024**3)
        summary = (
            f"[bold cyan]{info.operating_system}[/bold cyan]  "
            f"{info.os_version}  "
            f"Arch [bold]{info.architecture}[/bold]  "
            f"CPU {cpu_count} threads  RAM {memory_gib:.1f} GiB  "
            f"Managers: {managers}  "
            f"eSim: {info.esim_path or 'not detected'}  "
            f"[bold yellow]SAFE MODE: {'ON' if self.safe_mode else 'OFF'}[/bold yellow]"
        )
        self._main_screen().query_one("#header-bar", Static).update(summary)

    def action_toggle_safe_mode(self) -> None:
        if not self.safe_mode and self.install_in_progress:
            self.logger.warning("Safe Mode cannot be enabled during an active installation.")
            self.notify(
                "Cancel the active installation before enabling Safe Mode.",
                severity="warning",
            )
            return
        self.safe_mode = not self.safe_mode
        if self.system_info is not None:
            self._render_header(self.system_info)
        else:
            state = "ON" if self.safe_mode else "OFF"
            self._main_screen().query_one("#header-bar", Static).update(
                f"[bold yellow]SAFE MODE: {state}[/bold yellow]"
            )
        state = "ON" if self.safe_mode else "OFF"
        self._main_screen().query_one("#keys", Static).update(
            "s Scan   i Install   u Update   b Install All Missing   "
            "c Configure Env   "
            f"m Safe Mode: {state}   x Cancel operation   / Filter   q Quit"
        )
        self.logger.info("Safe Mode toggled %s.", state)
        self.notify(f"Safe Mode {state}")

    def _render_table(self, entries) -> None:
        main_screen = self._main_screen()
        table = main_screen.query_one("#dependency-table", DataTable)
        table.clear()
        for entry in entries:
            display_status = (
                "UPDATE AVAILABLE"
                if entry.available_version
                else entry.status.upper()
            )
            color = (
                "yellow"
                if entry.available_version
                else STATUS_COLORS.get(entry.status, "grey62")
            )
            icon = {
                "installed": "✔",
                "missing": "●",
                "outdated": "▲",
                "incompatible": "✖",
                "misconfigured": "▲",
                "unknown": "●",
                "unsupported": "—",
                "failed": "✖",
            }.get(entry.status, "●")
            table.add_row(
                entry.name,
                Text(f"{icon} {display_status}", style=f"bold {color}"),
                (
                    f"{entry.installed_version or '?'} → {entry.available_version}"
                    if entry.available_version
                    else entry.installed_version or "-"
                ),
                key=entry.id,
            )
        if entries:
            selected_row = next(
                (index for index, entry in enumerate(entries) if entry.id == self.selected_id),
                0,
            )
            table.move_cursor(row=selected_row)
            self.selected_id = entries[selected_row].id
            self._render_detail(entries[selected_row])
        elif self.report is not None:
            main_screen.query_one("#detail", Static).update(
                "No dependencies match this filter."
            )
        if self.report is not None:
            counts = self.report.counts
            summary = (
                f"Total {len(self.report.entries)}    "
                f"[green]✔ Installed {counts.get('installed', 0)}[/green]    "
                f"[yellow]▲ Outdated {counts.get('outdated', 0)}[/yellow]    "
                f"[yellow]↑ Updates "
                f"{sum(bool(entry.available_version) for entry in self.report.entries)}[/yellow]    "
                f"[red]● Missing {counts.get('missing', 0)}[/red]    "
                f"[red]✖ Incompatible {counts.get('incompatible', 0)}[/red]"
            )
            main_screen.query_one("#status-strip", Static).update(summary)

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id != "search" or self.report is None:
            return
        query = event.value.strip().lower()
        filtered = [
            entry for entry in self.entries
            if not query
            or query
            in (
                f"{entry.name} {entry.status} {entry.detail} "
                f"{'update available' if entry.available_version else ''} "
                f"{entry.available_version or ''}"
            ).lower()
        ]
        self._render_table(filtered)

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if isinstance(self.screen, ModalScreen):
            return
        key = getattr(event.row_key, "value", None)
        self.selected_id = key
        self._show_entry(key)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if isinstance(self.screen, ModalScreen):
            return
        key = getattr(event.row_key, "value", None)
        self.selected_id = key
        self._show_entry(key)

    def _show_entry(self, dependency_id: str | None) -> None:
        if dependency_id is None:
            return
        entry = next((item for item in self.entries if item.id == dependency_id), None)
        if entry:
            self._render_detail(entry)

    def _render_detail(self, entry: CompatibilityResult) -> None:
        path = str(entry.path) if entry.path else "Not detected"
        constraints = self._constraints(entry.id)
        command = self._planned_command(entry)
        color = STATUS_COLORS.get(entry.status, "grey62")
        content = (
            f"[bold]{entry.name}[/bold]\n\n"
            f"Status: [{color}]{entry.status.upper()}[/{color}]\n"
            f"Detected: {entry.installed_version or 'Unknown'}\n"
            f"Install path: {path}\n\n"
            f"Available update: {entry.available_version or 'Not checked'}\n\n"
            "[bold]Compatibility Constraints[/bold]\n"
            f"{constraints}\n\n"
            "[bold]Planned Install / Fix[/bold]\n"
            f"[cyan]{command}[/cyan]\n\n"
            f"[bold]Detail[/bold]\n{entry.detail}"
        )
        self._main_screen().query_one("#detail", Static).update(content)

    def _constraints(self, dependency_id: str) -> str:
        manifest = ScanService(self.manifest_path)
        from toolmate.core.manifest_manager import ManifestManager
        data = ManifestManager(manifest.manifest_path).load()
        dependency = next(
            (item for item in data["dependencies"] if item["id"] == dependency_id),
            None,
        )
        if dependency is None:
            return "None"
        version = dependency.get("version") or {}
        minimum = version.get("minimum") or "Any"
        maximum = version.get("maximum") or "Any"
        excluded = ", ".join(version.get("excluded") or []) or "None"
        return f"Minimum: {minimum}\nMaximum: {maximum}\nExcluded: {excluded}"

    def _planned_command(self, entry: CompatibilityResult) -> str:
        command, source = InstallService(self.manifest_path).plan(entry.id)
        return f"{' '.join(command)}  [{source}]"

    def _planned_update_command(self, entry: CompatibilityResult) -> str:
        command, source = UpdateService(self.manifest_path).plan(entry.id)
        return f"{' '.join(command)}  [{source}]"

    def action_filter(self) -> None:
        self.query_one("#search", Input).focus()

    async def action_update(self) -> None:
        if self.report is None:
            self.notify("Run a scan before checking for updates.", severity="warning")
            return
        if self.install_in_progress:
            self.notify("Another system operation is already running.", severity="warning")
            return
        try:
            service = UpdateService(self.manifest_path)
            updates = await asyncio.to_thread(service.check_available)
            self.entries = [
                replace(entry, available_version=updates.get(entry.id))
                for entry in self.report.entries
            ]
            self.report = replace(self.report, entries=tuple(self.entries))
            self._render_table(self.entries)
        except Exception as exc:
            self.logger.exception("Could not check for package updates.")
            self.notify(f"Update check failed: {exc}", severity="error")
            return

        self.logger.info("Update check completed: available=%d", len(updates))
        if not updates:
            self.notify("No updates are available from the supported package manager.")
            return
        entry = next(
            (item for item in self.entries if item.id == self.selected_id),
            None,
        )
        if entry is None or entry.available_version is None:
            self.notify(
                f"Found {len(updates)} available update(s); select an updated tool.",
                severity="information",
            )
            return
        try:
            command = self._planned_update_command(entry)
        except Exception as exc:
            self.logger.exception("Could not plan update for %s.", entry.id)
            self.notify(f"Could not plan update: {exc}", severity="error")
            return
        if self.safe_mode:
            self.logger.info(
                "Safe Mode update preview for %s: %s",
                entry.id,
                command,
            )
            self.push_screen(
                SafeModePreviewScreen(
                    f"Update preview: {entry.name}",
                    ((entry.name, command),),
                )
            )
            return
        self.logger.info("Update command preview for %s: %s", entry.id, command)
        self.push_screen(
            UpdateConfirmScreen(entry.name, command),
            callback=lambda approved: self._on_update_confirmation(entry, approved),
        )

    def action_configure_environment(self) -> None:
        if self.system_info is None or self.report is None:
            self.notify("Run a scan before configuring the environment.", severity="warning")
            return
        if self.install_in_progress:
            self.notify("Another system operation is already running.", severity="warning")
            return
        try:
            service = EnvironmentConfigurationService(self.manifest_path)
            plan = service.plan(self.system_info, self.entries)
        except Exception as exc:
            self.logger.exception("Could not plan environment configuration.")
            self.notify(f"Could not configure environment: {exc}", severity="error")
            return

        preview = plan.preview()
        if self.safe_mode:
            self.logger.info("Safe Mode environment configuration preview:\n%s", preview)
            self.push_screen(
                SafeModePreviewScreen(
                    "Configure environment preview",
                    (("User environment", preview),),
                )
            )
            return

        self.logger.info("Environment configuration plan:\n%s", preview)
        self.push_screen(
            EnvironmentConfirmScreen(plan),
            callback=lambda approved: self._on_environment_confirmation(
                service,
                plan,
                approved,
            ),
        )

    def action_install(self) -> None:
        if not self.report:
            self.notify("Run a scan before installation.", severity="warning")
            return
        if self.install_in_progress:
            self.notify("An installation is already running.", severity="warning")
            return
        if self.selected_id is None:
            self.notify("Select a dependency.", severity="warning")
            return
        entry = next(
            (item for item in self.entries if item.id == self.selected_id),
            None,
        )
        if entry is None:
            return
        try:
            command = self._planned_command(entry)
        except Exception as exc:
            self.logger.exception("Could not plan installation for %s.", entry.id)
            self.notify(f"Could not plan installation: {exc}", severity="error")
            return
        if self.safe_mode:
            self.logger.info("Safe Mode install preview for %s: %s", entry.id, command)
            self.push_screen(
                SafeModePreviewScreen(
                    f"Install preview: {entry.name}",
                    ((entry.name, command),),
                )
            )
            return
        self.logger.info("Install command preview for %s: %s", entry.id, command)
        self.push_screen(
            InstallConfirmScreen(entry.name, command),
            callback=lambda approved: self._on_install_confirmation(entry, approved),
        )

    def action_install_all_missing(self) -> None:
        if self.report is None:
            self.notify("Run a scan before installation.", severity="warning")
            return
        if self.install_in_progress:
            self.notify("An installation is already running.", severity="warning")
            return

        try:
            service = InstallService(self.manifest_path)
            items = tuple(
                (entry, self._planned_command(entry))
                for entry in self.report.entries
                if entry.status == "missing"
                and service.can_install_automatically(entry.id)
            )
        except Exception as exc:
            self.logger.exception("Could not build the batch installation plan.")
            self.notify(f"Could not plan batch installation: {exc}", severity="error")
            return
        if not items:
            self.notify(
                "No missing dependencies have a supported automated installer.",
                severity="warning",
            )
            return
        for entry, command in items:
            self.logger.info(
                "%s batch install command preview for %s: %s",
                "Safe Mode" if self.safe_mode else "Confirmed",
                entry.id,
                command,
            )
        if self.safe_mode:
            self.push_screen(
                SafeModePreviewScreen(
                    "Install All Missing preview",
                    tuple((entry.name, command) for entry, command in items),
                )
            )
            return
        self.push_screen(
            InstallAllConfirmScreen(items),
            callback=lambda approved: self._on_batch_install_confirmation(
                tuple(entry for entry, _ in items), approved
            ),
        )

    def _on_install_confirmation(
        self,
        entry: CompatibilityResult,
        approved: bool | None,
    ) -> None:
        if approved and self.safe_mode:
            self.logger.info(
                "Safe Mode blocked execution of the selected install for %s.",
                entry.id,
            )
            self.notify("Safe Mode is ON; installation was not executed.")
            return
        if approved and not self.install_in_progress:
            self.install_in_progress = True
            self.run_worker(self._run_installation(entry))

    def _on_batch_install_confirmation(
        self,
        entries: tuple[CompatibilityResult, ...],
        approved: bool | None,
    ) -> None:
        if approved and self.safe_mode:
            self.logger.info(
                "Safe Mode blocked execution of a batch containing %d dependencies.",
                len(entries),
            )
            self.notify("Safe Mode is ON; batch installation was not executed.")
            return
        if approved and not self.install_in_progress:
            self.install_in_progress = True
            self.run_worker(self._run_batch_installations(entries))

    def _on_update_confirmation(
        self,
        entry: CompatibilityResult,
        approved: bool | None,
    ) -> None:
        if approved and self.safe_mode:
            self.logger.info("Safe Mode blocked update execution for %s.", entry.id)
            self.notify("Safe Mode is ON; update was not executed.")
            return
        if approved and not self.install_in_progress:
            self.install_in_progress = True
            self.run_worker(self._run_update(entry))

    def _on_environment_confirmation(
        self,
        service: EnvironmentConfigurationService,
        plan: EnvironmentPlan,
        approved: bool | None,
    ) -> None:
        if approved and self.safe_mode:
            self.logger.info("Safe Mode blocked environment configuration.")
            self.notify("Safe Mode is ON; environment was not modified.")
            return
        if approved and not self.install_in_progress:
            self.install_in_progress = True
            self.run_worker(self._run_environment_configuration(service, plan))

    async def _run_update(self, entry: CompatibilityResult) -> None:
        output = self.query_one("#install-output", RichLog)
        output.clear()
        output.write(f"Starting update for {entry.name}...")
        cancel_event = Event()
        self.active_install_cancel = cancel_event

        def stream_output(line: str) -> None:
            self.logger.info("Update output for %s: %s", entry.id, line)
            self.call_from_thread(output.write, line)

        try:
            service = UpdateService(self.manifest_path)
            result = await asyncio.to_thread(
                service.execute,
                entry.id,
                True,
                stream_output,
                cancel_event,
            )
        except Exception as exc:
            self.logger.exception("Update failed for %s.", entry.id)
            output.write(f"Update failed to start: {exc}")
            self.notify(f"Update failed: {exc}", severity="error")
            return
        finally:
            self.active_install_cancel = None
            self.install_in_progress = False

        if result.cancelled:
            self.logger.warning("Update cancelled for %s.", entry.id)
            output.write("Update cancelled.")
            self.notify("Update cancelled.", severity="warning")
        elif result.succeeded:
            self.logger.info("Update completed for %s.", entry.id)
            output.write("Update completed successfully.")
            self.notify("Update completed.")
        else:
            self.logger.error(
                "Update failed for %s with exit code %s.",
                entry.id,
                result.exit_code,
            )
            output.write(f"Update exited with code {result.exit_code}.")
            self.notify("Update completed with errors.", severity="warning")
        await self.action_scan()

    async def _run_environment_configuration(
        self,
        service: EnvironmentConfigurationService,
        plan: EnvironmentPlan,
    ) -> None:
        output = self.query_one("#install-output", RichLog)
        output.clear()
        try:
            backup = await asyncio.to_thread(service.apply, plan, True)
        except Exception as exc:
            self.logger.exception("Environment configuration failed.")
            output.write(f"Environment configuration failed: {exc}")
            self.notify(f"Environment configuration failed: {exc}", severity="error")
            return
        finally:
            self.install_in_progress = False

        self.logger.info("Environment configured; backup saved to %s.", backup)
        output.write(f"Environment configured. Backup: {backup}")
        output.write("Open a new terminal session to use the updated environment.")
        self.notify("Environment configured. Restart the terminal to apply changes.")

    async def _run_installation(self, entry: CompatibilityResult) -> None:
        if self.safe_mode:
            self.logger.info(
                "Safe Mode prevented selected installation for %s.",
                entry.id,
            )
            self.install_in_progress = False
            self.notify("Safe Mode is ON; installation was not executed.")
            return
        output = self.query_one("#install-output", RichLog)
        output.clear()
        output.write(f"Starting installation for {entry.name}...")
        cancel_event = Event()
        self.active_install_cancel = cancel_event

        def stream_output(line: str) -> None:
            self.logger.info("Installer output for %s: %s", entry.id, line)
            self.call_from_thread(output.write, line)

        try:
            service = InstallService(self.manifest_path)
            self.logger.info("Starting approved installation for %s.", entry.id)
            result = await asyncio.to_thread(
                service.execute,
                entry.id,
                True,
                stream_output,
                cancel_event,
            )
        except Exception as exc:
            self.logger.exception("Installation failed for %s.", entry.id)
            output.write(f"Installation failed to start: {exc}")
            self.notify(f"Installation failed: {exc}", severity="error")
            return
        finally:
            self.active_install_cancel = None
            self.install_in_progress = False

        if result.cancelled:
            self.logger.warning("Installation cancelled for %s.", entry.id)
            output.write("Operation cancelled.")
            self.notify("Operation cancelled", severity="warning")
        elif result.succeeded:
            self.logger.info("Installation completed for %s.", entry.id)
            output.write("Installation completed successfully.")
            self.notify("Installation completed")
        else:
            self.logger.error(
                "Installation failed for %s with exit code %s.",
                entry.id,
                result.exit_code,
            )
            output.write(f"Installation exited with code {result.exit_code}.")
            self.notify("Installation completed with errors", severity="warning")

        await self.action_scan()

    async def _run_batch_installations(
        self,
        entries: tuple[CompatibilityResult, ...],
    ) -> None:
        if self.safe_mode:
            self.logger.info(
                "Safe Mode prevented batch installation for %d dependencies.",
                len(entries),
            )
            self.install_in_progress = False
            self.notify("Safe Mode is ON; batch installation was not executed.")
            return
        output = self.query_one("#install-output", RichLog)
        output.clear()
        cancel_event = Event()
        self.active_install_cancel = cancel_event
        succeeded = 0
        failed = 0
        cancelled = False

        def stream_output(line: str) -> None:
            self.logger.info("Batch installer output: %s", line)
            self.call_from_thread(output.write, line)

        try:
            service = InstallService(self.manifest_path)
            for entry in entries:
                if cancel_event.is_set():
                    cancelled = True
                    self.logger.warning(
                        "Batch installation cancelled before %s; remaining installs skipped.",
                        entry.id,
                    )
                    output.write("Cancellation requested; remaining installs were skipped.")
                    break

                try:
                    command = self._planned_command(entry)
                except Exception as exc:
                    failed += 1
                    self.logger.exception(
                        "Could not plan batch installation for %s.",
                        entry.id,
                    )
                    output.write(f"{entry.name} failed: {exc}")
                    continue
                output.write(f"Starting installation for {entry.name}: {command}")
                self.logger.info("Starting approved batch installation for %s.", entry.id)
                try:
                    result = await asyncio.to_thread(
                        service.execute,
                        entry.id,
                        True,
                        stream_output,
                        cancel_event,
                    )
                except Exception as exc:
                    failed += 1
                    self.logger.exception("Batch installation failed for %s.", entry.id)
                    output.write(f"{entry.name} failed: {exc}")
                    continue

                if result.cancelled:
                    cancelled = True
                    self.logger.warning("Batch installation cancelled for %s.", entry.id)
                    output.write(f"{entry.name} installation was cancelled.")
                    break
                if result.succeeded:
                    succeeded += 1
                    self.logger.info("Batch installation completed for %s.", entry.id)
                    output.write(f"{entry.name} installation completed.")
                else:
                    failed += 1
                    self.logger.error(
                        "Batch installation failed for %s with exit code %s.",
                        entry.id,
                        result.exit_code,
                    )
                    output.write(
                        f"{entry.name} installation exited with code "
                        f"{result.exit_code}."
                    )
        except Exception as exc:
            failed += 1
            self.logger.exception("Batch installation could not start.")
            output.write(f"Batch installation failed to start: {exc}")
        finally:
            self.active_install_cancel = None
            self.install_in_progress = False

        not_completed = len(entries) - succeeded - failed
        self.logger.info(
            "Batch installation finished: succeeded=%d failed=%d not_completed=%d cancelled=%s",
            succeeded,
            failed,
            not_completed,
            cancelled,
        )
        output.write(
            f"Batch finished: {succeeded} succeeded, {failed} failed, "
            f"{not_completed} not completed."
        )
        if cancelled:
            self.notify("Batch installation cancelled.", severity="warning")
        elif failed:
            self.notify(
                f"Batch finished: {succeeded} succeeded, {failed} failed.",
                severity="warning",
            )
        else:
            self.notify(f"Installed {succeeded} dependencies.")
        await self.action_scan()

    def action_cancel_install(self) -> None:
        if self.active_install_cancel is None:
            self.notify("No cancellable operation is running.", severity="warning")
            return
        self.active_install_cancel.set()
        self.notify("Cancellation requested. Waiting for the process to stop.")


def main() -> int:
    ToolMateApp().run()
    return 0
