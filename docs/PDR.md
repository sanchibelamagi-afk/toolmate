# ToolMate Product Design Requirements

ToolMate is a cross-platform terminal application for detecting, diagnosing, and preparing
the dependencies required by eSim.

The user interface uses Textual for the full-screen interactive TUI and Rich for terminal
formatted output. It provides a system header, searchable dependency pane, compatibility
status badges, selected-dependency details, and explicit installation confirmation.

The TUI remains separate from system detection, manifest loading, dependency scanning,
compatibility evaluation, and future installation services. Backend services are reusable
by both the TUI and CLI.

The supported executable entry point is the `toolmate` command, installed from the
project's `pyproject.toml` script declaration.

Installation is an explicit, approved operation. The TUI confirms the package command,
streams process output live, reports success or failure, and automatically re-runs the
environment scan after execution.

The dashboard uses a dark slate palette, rounded titled panes, a system/resource header,
and a summary strip for total, installed, outdated, missing, and incompatible dependencies.
Windows package identifiers are sourced from available catalogs; dependencies without
Winget packages provide a verified Chocolatey or official download fallback when available.

Downloads are HTTPS-only and are accepted only when a manifest SHA-256 checksum matches.
Cancellation is supported for active downloads and package-manager processes where the
underlying process can be stopped safely.
