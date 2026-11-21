┌─────────────────────────────────────────────┐
│              TOOLMATE TUI                  │
│               Textual + Rich                │
│                                             │
│  System Overview │ Dependencies │ Details  │
│  Scan [s] │ Install [i] │ Filter [/]      │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│             APPLICATION LAYER              │
│                                             │
│  Scan Manager                              │
│  Installation Manager                       │
│  Fix All Workflow                            │
│  Compatibility Manager                       │
│  Verification Manager                       │
│  Diagnostic Manager                          │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│              CORE ENGINE                   │
│                                             │
│  Dependency Detection                       │
│  Manifest Parser                            │
│  Version Comparison                         │
│  Dependency Resolver                        │
│  Task Orchestrator                          │
│  Permission Manager                          │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│          PLATFORM ABSTRACTION              │
│                                             │
│ Windows       Linux       macOS             │
│ Winget        APT         Homebrew           │
│ Chocolatey    pacman      Pip / POSIX profile│
│ User PATH     Linux paths macOS paths        │
│ UAC           Sudo        User environment   │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│          OPERATING SYSTEM                  │
│                                             │
│ Applications │ Packages │ Files │ Config    │
└─────────────────────────────────────────────┘

The terminal UI uses rounded Tokyo-Night/dark-slate panels for System Overview,
Dependencies, Package Details, and Install Output. The dependency list is searchable,
and the status strip summarizes total, installed, outdated, missing, and incompatible
items. System detection, scanning, compatibility, and installation remain in backend
services; TUI widgets only display results, request confirmation, and invoke services.
The `[b] Install All Missing` action uses the installation service to plan eligible
missing dependencies, presents every command for one explicit approval, then executes
the batch sequentially. An individual failure is reported without blocking later
independent operations, and a final scan verifies the resulting environment.
The application configures a persistent `logs/toolmate.log` handler and records scans,
command previews, installer output, operation outcomes, and errors.
The versioned manifest defines the 12-tool eSim environment, including executable,
path-based, and external-service detection. Safe Mode is owned by the TUI as a
presentation/runtime guard: it displays and logs the installation plan but never calls
an installer until Safe Mode is switched off and the user approves a plan.
The update service queries the platform package manager for available versions and
executes only a user-confirmed upgrade. The environment configuration service builds
the exact proposed user PATH and `ESIM_HOME` changes, rejects profiles changed since
preview, and creates a backup before writing. Windows changes are limited to the
current user's Environment registry key; Linux uses `~/.profile`, and macOS uses
`~/.zprofile`. TUI widgets display these plans and confirmations but do not modify
the environment or invoke package-manager commands directly.

The installable Python package uses the `src/toolmate` package layout and exposes
`toolmate.cli:main` through the `toolmate` console script. Manifest-declared downloads
must use HTTPS and a configured SHA-256 digest; downloaded artifacts are verified before
being made available and are not launched automatically. Active package processes and
downloads accept cooperative cancellation where supported.
The eSim adapter exposes a non-interactive JSON compatibility report and accepts an
explicit eSim root plus configured dependency paths. The eSim application can launch the
TUI or bind its Check Dependencies menu item to those CLI options without coupling eSim
code to ToolMate internals.
Setuptools installs the canonical manifest under `share/toolmate/config` for wheel
installations; source checkouts continue to load `config/manifest.yaml`. GitHub Actions
runs tests and Ruff on Windows, Linux, and macOS and builds wheel/source artifacts on
each platform. The macOS platform adapter detects Homebrew and eSim roots; package
installation, version queries, update checks, and upgrades use Homebrew when a formula
is present in the manifest.
