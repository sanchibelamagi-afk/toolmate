import asyncio
from threading import Event

import psutil
from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
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
from toolmate.services.scan_service import ScanService
from toolmate.services.install_service import InstallService


STATUS_COLORS = {
    "installed": "green",
    "missing": "red",
    "outdated": "yellow",
    "incompatible": "red",
    "misconfigured": "magenta",
    "unknown": "grey62",
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
    """

    BINDINGS = [
        Binding("s", "scan", "[s] Scan"),
        Binding("i", "install", "[i] Install"),
        Binding("b", "install_all_missing", "[b] Install All Missing"),
        Binding("x", "cancel_install", "[x] Cancel install"),
        Binding("slash", "filter", "[/] Filter"),
        Binding("q", "quit", "[q] Quit"),
    ]

    def __init__(self, manifest_path: str = "config/manifest.yaml") -> None:
        super().__init__()
        self.manifest_path = manifest_path
        self.report: CompatibilityReport | None = None
        self.entries = []
        self.selected_id: str | None = None
        self.active_install_cancel: Event | None = None
        self.install_in_progress = False

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
            "s Scan   i Install   b Install All Missing   x Cancel   / Filter   q Quit",
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
        try:
            info, report = await asyncio.to_thread(self._scan)
        except Exception as exc:
            self.notify(f"Scan failed: {exc}", severity="error")
            return
        self.report = report
        self.entries = list(report.entries)
        self._render_header(info)
        self._render_table(self.entries)
        self.notify("Scan complete")

    def _scan(self) -> tuple[SystemInfo, CompatibilityReport]:
        info = detect_system_info()
        report = ScanService(self.manifest_path).evaluate()
        return info, report

    def _render_header(self, info: SystemInfo) -> None:
        managers = ", ".join(info.package_managers) if info.package_managers else "None"
        cpu_count = psutil.cpu_count(logical=True) or "Unknown"
        memory_gib = psutil.virtual_memory().total / (1024**3)
        summary = (
            f"[bold cyan]{info.operating_system}[/bold cyan]  "
            f"{info.os_version}  "
            f"Arch [bold]{info.architecture}[/bold]  "
            f"CPU {cpu_count} threads  RAM {memory_gib:.1f} GiB  "
            f"Managers: {managers}  "
            f"eSim: {info.esim_path or 'not detected'}"
        )
        self.query_one("#header-bar", Static).update(summary)

    def _render_table(self, entries) -> None:
        table = self.query_one("#dependency-table", DataTable)
        table.clear()
        for entry in entries:
            color = STATUS_COLORS.get(entry.status, "grey62")
            icon = {
                "installed": "✔",
                "missing": "●",
                "outdated": "▲",
                "incompatible": "✖",
                "misconfigured": "▲",
                "unknown": "●",
                "failed": "✖",
            }.get(entry.status, "●")
            table.add_row(
                entry.name,
                Text(f"{icon} {entry.status.upper()}", style=f"bold {color}"),
                entry.installed_version or "-",
                key=entry.id,
            )
        if entries:
            table.move_cursor(row=0)
            self._render_detail(entries[0])
        elif self.report is not None:
            self.query_one("#detail", Static).update("No dependencies match this filter.")
        if self.report is not None:
            counts = self.report.counts
            summary = (
                f"Total {len(self.report.entries)}    "
                f"[green]✔ Installed {counts.get('installed', 0)}[/green]    "
                f"[yellow]▲ Outdated {counts.get('outdated', 0)}[/yellow]    "
                f"[red]● Missing {counts.get('missing', 0)}[/red]    "
                f"[red]✖ Incompatible {counts.get('incompatible', 0)}[/red]"
            )
            self.query_one("#status-strip", Static).update(summary)

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id != "search" or self.report is None:
            return
        query = event.value.strip().lower()
        filtered = [
            entry for entry in self.entries
            if not query or query in f"{entry.name} {entry.status} {entry.detail}".lower()
        ]
        self._render_table(filtered)

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        key = getattr(event.row_key, "value", None)
        self.selected_id = key
        self._show_entry(key)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
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
            "[bold]Compatibility Constraints[/bold]\n"
            f"{constraints}\n\n"
            "[bold]Planned Install / Fix[/bold]\n"
            f"[cyan]{command}[/cyan]\n\n"
            f"[bold]Detail[/bold]\n{entry.detail}"
        )
        self.query_one("#detail", Static).update(content)

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

    def action_filter(self) -> None:
        self.query_one("#search", Input).focus()

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
        self.push_screen(
            InstallConfirmScreen(entry.name, self._planned_command(entry)),
            callback=lambda approved: self._on_install_confirmation(entry, approved),
        )

    def action_install_all_missing(self) -> None:
        if self.report is None:
            self.notify("Run a scan before installation.", severity="warning")
            return
        if self.install_in_progress:
            self.notify("An installation is already running.", severity="warning")
            return

        service = InstallService(self.manifest_path)
        items = tuple(
            (entry, self._planned_command(entry))
            for entry in self.report.entries
            if entry.status == "missing"
            and service.can_install_automatically(entry.id)
        )
        if not items:
            self.notify(
                "No missing dependencies have a supported automated installer.",
                severity="warning",
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
        if approved and not self.install_in_progress:
            self.install_in_progress = True
            self.run_worker(self._run_installation(entry))

    def _on_batch_install_confirmation(
        self,
        entries: tuple[CompatibilityResult, ...],
        approved: bool | None,
    ) -> None:
        if approved and not self.install_in_progress:
            self.install_in_progress = True
            self.run_worker(self._run_batch_installations(entries))

    async def _run_installation(self, entry: CompatibilityResult) -> None:
        output = self.query_one("#install-output", RichLog)
        output.clear()
        output.write(f"Starting installation for {entry.name}...")
        service = InstallService(self.manifest_path)
        cancel_event = Event()
        self.active_install_cancel = cancel_event

        def stream_output(line: str) -> None:
            self.call_from_thread(output.write, line)

        try:
            result = await asyncio.to_thread(
                service.execute,
                entry.id,
                True,
                stream_output,
                cancel_event,
            )
        except Exception as exc:
            output.write(f"Installation failed to start: {exc}")
            self.notify(f"Installation failed: {exc}", severity="error")
            return
        finally:
            self.active_install_cancel = None
            self.install_in_progress = False

        if result.cancelled:
            output.write("Operation cancelled.")
            self.notify("Operation cancelled", severity="warning")
        elif result.succeeded:
            output.write("Installation completed successfully.")
            self.notify("Installation completed")
        else:
            output.write(f"Installation exited with code {result.exit_code}.")
            self.notify("Installation completed with errors", severity="warning")

        await self.action_scan()

    async def _run_batch_installations(
        self,
        entries: tuple[CompatibilityResult, ...],
    ) -> None:
        output = self.query_one("#install-output", RichLog)
        output.clear()
        service = InstallService(self.manifest_path)
        cancel_event = Event()
        self.active_install_cancel = cancel_event
        succeeded = 0
        failed = 0
        cancelled = False

        def stream_output(line: str) -> None:
            self.call_from_thread(output.write, line)

        try:
            for entry in entries:
                if cancel_event.is_set():
                    cancelled = True
                    output.write("Cancellation requested; remaining installs were skipped.")
                    break

                command = self._planned_command(entry)
                output.write(f"Starting installation for {entry.name}: {command}")
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
                    output.write(f"{entry.name} failed: {exc}")
                    continue

                if result.cancelled:
                    cancelled = True
                    output.write(f"{entry.name} installation was cancelled.")
                    break
                if result.succeeded:
                    succeeded += 1
                    output.write(f"{entry.name} installation completed.")
                else:
                    failed += 1
                    output.write(
                        f"{entry.name} installation exited with code "
                        f"{result.exit_code}."
                    )
        finally:
            self.active_install_cancel = None
            self.install_in_progress = False

        output.write(
            f"Batch finished: {succeeded} succeeded, {failed} failed, "
            f"{len(entries) - succeeded - failed} not completed."
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
