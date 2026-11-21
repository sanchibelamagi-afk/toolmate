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
│ Windows              Linux                  │
│ Winget               APT                    │
│ Chocolatey            pacman                │
│                      Pip                    │
│ Windows Paths         Linux Paths           │
│ UAC                   Sudo                   │
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

The installable Python package uses the `src/toolmate` package layout and exposes
`toolmate.cli:main` through the `toolmate` console script. Manifest-declared downloads
must use HTTPS and a configured SHA-256 digest; downloaded artifacts are verified before
being made available and are not launched automatically. Active package processes and
downloads accept cooperative cancellation where supported.
