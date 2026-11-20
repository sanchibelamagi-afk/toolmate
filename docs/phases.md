# ToolMate
## Implementation Plan, File Structure & Dependencies

**Project:** eSim ToolMate  
**Version:** 0.1  
**Based on:** ToolMate PDR v0.1  
**Architecture:** Modular desktop application  
**Language:** Python 3  
**TUI:** Textual + Rich  

---

# 1. Implementation Strategy

ToolMate will be developed incrementally. Each phase will produce a working, testable component before the next phase begins.

The application will follow a modular architecture with separation between:

- User interface
- Application logic
- Dependency detection
- Compatibility validation
- Installation
- Verification
- Operating system interaction
- Configuration and manifest
- Logging and diagnostics
- Local database

## Development principles

1. Implement one feature at a time.
2. Keep GUI code separate from core logic.
3. Never execute system commands directly from GUI widgets.
4. Never hardcode dependency requirements into the scanner.
5. Use the manifest as the source of dependency requirements.
6. Use platform-specific adapters for Windows and Linux.
7. Make system-changing operations explicit and user-approved.
8. Verify every installation.
9. Test functionality before integrating the next module.
10. Keep the application runnable throughout development.

---

# 2. Implementation Phases

## Phase 0: Project Foundation

### Objective
Establish the project structure, development environment, coding rules, and configuration system.

### Tasks

- Create the repository structure.
- Create Python virtual environment.
- Configure dependencies.
- Create application entry point.
- Configure logging.
- Create manifest loader.
- Add initial manifest schema.
- Create basic application window.

### Deliverable

ToolMate launches successfully with an empty dashboard.

---

## Phase 1: System Detection

### Objective
Understand the user's environment.

### Features

- [x] Detect OS.
- [x] Detect OS version.
- [x] Detect CPU architecture.
- [x] Detect package manager.
- [x] Detect administrator status.
- [x] Locate eSim installation.
- [x] Detect available environment variables.

### Modules

- [x] System detector
- [x] Platform detector
- [x] Package manager detector
- [x] eSim locator

### Deliverable

**Status:** [x] A system information screen showing detected environment details.

---

## Phase 2: Dependency Scanner

### Objective
Identify dependencies installed on the system.

### Features

- [x] Scan dependencies from manifest.
- [x] Detect executable locations.
- [x] Detect installed versions.
- [x] Detect Python packages.
- [x] Detect multiple installations.
- [x] Handle failed detection.

### Detection methods

1. [x] Executable search through PATH.
2. [x] Known installation paths.
3. [x] Package manager query.
4. [x] Python package detection.
5. [x] Registry detection on Windows, where appropriate.
6. [x] Manifest-defined custom detection.

### Deliverable

**Status:** [x] A dependency inventory showing name, version, path, and detection result.

---

## Phase 3: Compatibility Engine

### Objective
Determine whether detected dependencies meet eSim requirements.

### Features

- [x] Parse version constraints.
- [x] Compare installed versions.
- [x] Identify missing dependencies.
- [x] Identify outdated dependencies.
- [x] Identify incompatible dependencies.
- [x] Identify misconfigured dependencies.
- [x] Detect unknown versions.

### Deliverable

**Status:** [x] A compatibility report for the entire environment.

---

## Phase 4: Terminal Dashboard

### Objective
Present dependency health clearly.

### Features

- [x] Full-screen Textual dashboard.
- [x] Searchable/filterable dependency table.
- [x] Rich status indicators.
- [x] System information header.
- [x] Scan keybinding.
- [x] Refresh keybinding.
- [x] Dependency details pane.
- [x] Install confirmation modal.

### Deliverable

**Status:** [x] A usable GUI displaying live scan results.

---

## Phase 5: Installation Engine

### Objective
Install missing dependencies safely.

### Features

- [x] Installation source selection.
- [x] Package manager integration.
- [ ] Download manager.
- [ ] Checksum verification.
- [x] Installation planning.
- [x] User confirmation.
- [x] Permission handling.
- [x] Progress display.
- [ ] Cancellation where safe.

### Initial installation methods

**Linux**

- APT

**Windows**

- Winget
- Chocolatey, if required and supported

**Python**

- Pip
- Virtual environments where applicable

**Fallback**

- Official installer
- Verified vendor release

### Deliverable

**Status:** [x] Installation actions are planned and confirmed in the TUI with live output and post-install re-scan.

---

## Phase 6: Fix All

### Objective
Resolve multiple dependency problems through a single controlled workflow.

### Features

- Identify eligible dependencies.
- Build installation plan.
- Resolve installation order.
- Show summary.
- Request approval.
- Execute operations.
- Continue safely after independent failures.
- Verify each result.
- Generate final report.

### Deliverable

Functional Fix All workflow.

---

## Phase 7: Diagnostics and Reliability

### Objective
Improve troubleshooting and failure handling.

### Features

- Detailed logs.
- Retry policy.
- Error categorization.
- Diagnostic report export.
- Network failure handling.
- Permission failure handling.
- Package manager lock handling.
- Partial installation detection.

### Deliverable

ToolMate can diagnose and explain common failures.

---

## Phase 8: eSim Integration

### Objective
Connect ToolMate with the eSim application.

### Features

- Detect eSim configuration.
- Validate eSim dependency paths.
- Launch ToolMate from eSim.
- Add Check Dependencies entry.
- Share compatibility information.

### Deliverable

ToolMate accessible through eSim and independently.

---

## Phase 9: Packaging and Release

### Objective
Create distributable builds.

### Features

- Windows packaging.
- Linux packaging.
- Automated tests.
- Build pipeline.
- Versioning.
- Release documentation.

### Deliverable

Installable or distributable MVP builds.

---

# 3. Project File Structure

## Proposed directory structure

```text
toolmate/
│
├── main.py
├── README.md
├── LICENSE
├── requirements.txt
├── requirements-dev.txt
├── .gitignore
│
├── docs/
│   ├── PDR.md
│   ├── Architecture.md
│   ├── Design.md
│   ├── Rules.md
│   ├── Phases.md
│   └── Memory.md
│
├── config/
│   ├── manifest.yaml
│   └── manifest_schema.yaml
│
├── src/
│   └── toolmate/
│       ├── __init__.py
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── system_detector.py
│       │   ├── dependency_scanner.py
│       │   ├── compatibility_checker.py
│       │   ├── manifest_manager.py
│       │   ├── dependency_resolver.py
│       │   ├── task_manager.py
│       │   └── models.py
│       │
│       ├── services/
│       │   ├── __init__.py
│       │   ├── scan_service.py
│       │   ├── install_service.py
│       │   ├── verification_service.py
│       │   ├── diagnostic_service.py
│       │   └── update_service.py
│       │
│       ├── installers/
│       │   ├── __init__.py
│       │   ├── base_installer.py
│       │   ├── apt_installer.py
│       │   ├── winget_installer.py
│       │   ├── chocolatey_installer.py
│       │   ├── pip_installer.py
│       │   └── download_installer.py
│       │
│       ├── platform/
│       │   ├── __init__.py
│       │   ├── windows.py
│       │   ├── linux.py
│       │   ├── permissions.py
│       │   └── paths.py
│       │
│       ├── detection/
│       │   ├── __init__.py
│       │   ├── executable_detector.py
│       │   ├── python_package_detector.py
│       │   ├── package_manager_detector.py
│       │   └── registry_detector.py
│       │
│       ├── verification/
│       │   ├── __init__.py
│       │   ├── version_verifier.py
│       │   ├── executable_verifier.py
│       │   ├── import_verifier.py
│       │   └── smoke_tests.py
│       │
│       ├── storage/
│       │   ├── __init__.py
│       │   ├── database.py
│       │   ├── repositories.py
│       │   └── migrations.py
│       │
│       ├── diagnostics/
│       │   ├── __init__.py
│       │   ├── logger.py
│       │   └── report_generator.py
│       │
│       └── gui/
│           ├── __init__.py
│           ├── main_window.py
│           ├── dashboard.py
│           ├── dependency_view.py
│           ├── install_dialog.py
│           ├── confirmation_dialog.py
│           ├── settings_view.py
│           ├── log_viewer.py
│           ├── workers.py
│           └── widgets/
│               ├── __init__.py
│               ├── status_badge.py
│               ├── dependency_card.py
│               └── progress_widget.py
│
├── data/
│   └── .gitkeep
│
├── logs/
│   └── .gitkeep
│
├── cache/
│   └── .gitkeep
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   │
│   ├── unit/
│   │   ├── test_manifest_manager.py
│   │   ├── test_version_checker.py
│   │   ├── test_system_detector.py
│   │   ├── test_dependency_scanner.py
│   │   └── test_compatibility_checker.py
│   │
│   ├── integration/
│   │   ├── test_scan_pipeline.py
│   │   ├── test_install_pipeline.py
│   │   └── test_verification_pipeline.py
│   │
│   └── gui/
│       ├── test_dashboard.py
│       └── test_dialogs.py
│
└── packaging/
    ├── toolmate.spec
    ├── windows/
    └── linux/
```

---

# 4. Files to Create First

Do not create every file in this tree immediately. Empty files everywhere create the illusion of progress and a very impressive collection of nothing.

Create files in this order.

## Stage 1: Foundation

| File | Responsibility |
|---|---|
| `main.py` | Start application |
| `src/toolmate/__init__.py` | Package initialization |
| `src/toolmate/core/models.py` | Data structures |
| `src/toolmate/core/manifest_manager.py` | Read and validate manifest |
| `config/manifest.yaml` | Dependency definitions |
| `requirements.txt` | Runtime packages |
| `.gitignore` | Ignore generated files |

## Stage 2: System Detection

| File | Responsibility |
|---|---|
| `core/system_detector.py` | Detect OS and system details |
| `platform/windows.py` | Windows-specific operations |
| `platform/linux.py` | Linux-specific operations |
| `platform/paths.py` | Installation path handling |
| `detection/package_manager_detector.py` | Detect package managers |

## Stage 3: Scanner

| File | Responsibility |
|---|---|
| `core/dependency_scanner.py` | Scan dependencies |
| `detection/executable_detector.py` | Locate executable |
| `detection/python_package_detector.py` | Detect Python packages |
| `detection/registry_detector.py` | Detect Windows installations |
| `core/compatibility_checker.py` | Validate versions |

## Stage 4: GUI

| File | Responsibility |
|---|---|
| `gui/main_window.py` | Application shell |
| `gui/dashboard.py` | Main dashboard |
| `gui/dependency_view.py` | Dependency list |
| `gui/workers.py` | Background tasks |
| `gui/widgets/status_badge.py` | Status visualization |

## Stage 5: Installation

| File | Responsibility |
|---|---|
| `services/install_service.py` | Installation orchestration |
| `installers/base_installer.py` | Installer interface |
| `installers/apt_installer.py` | APT |
| `installers/winget_installer.py` | Winget |
| `installers/pip_installer.py` | Pip |
| `installers/download_installer.py` | Verified downloads |
| `services/verification_service.py` | Post-install verification |
| `platform/permissions.py` | Privilege management |

## Stage 6: Persistence and Diagnostics

| File | Responsibility |
|---|---|
| `storage/database.py` | SQLite connection |
| `storage/repositories.py` | Database operations |
| `diagnostics/logger.py` | Logging |
| `diagnostics/report_generator.py` | Export report |

## Stage 7: Testing and Release

| File | Responsibility |
|---|---|
| `tests/conftest.py` | Shared fixtures |
| `tests/unit/` | Unit tests |
| `tests/integration/` | Integration tests |
| `tests/gui/` | GUI tests |
| `packaging/toolmate.spec` | PyInstaller configuration |

---

# 5. Existing eSim Files to Change

## MVP

**No existing eSim files should be modified during the initial development phases.**

ToolMate should first function as an independent application.

This reduces risk because dependency scanning and installation can be developed and tested without breaking the eSim application itself.

## Later integration

Once ToolMate is stable, we may need to modify:

- eSim main application entry point
- eSim menu/navigation
- Dependency checking workflow
- eSim configuration or path management
- Packaging or distribution scripts

The exact files must be identified from the target eSim repository and release branch.

Changes should be isolated and documented.

---

# 6. Required Dependencies

Dependencies are divided into three categories:

1. Runtime Python packages
2. Development and testing packages
3. External system tools that ToolMate manages

---

## 6.1 Runtime Python dependencies

| Package | Purpose | Required |
|---|---|---|
| Textual | Terminal UI framework | Yes |
| Rich | Terminal rendering | Yes |
| PyYAML | YAML manifest parsing | Yes |
| packaging | Version comparison | Yes |
| psutil | System information | Recommended |
| requests | HTTP downloads | Recommended |
| platformdirs | OS-specific application directories | Recommended |

### Python standard library

We do not need to install these separately.

| Module | Purpose |
|---|---|
| `subprocess` | Execute system commands |
| `pathlib` | Paths |
| `platform` | OS information |
| `shutil` | Executable discovery |
| `sqlite3` | Database |
| `logging` | Logs |
| `json` | Structured data |
| `hashlib` | Checksum validation |
| `threading` | Threads |
| `concurrent.futures` | Task execution |
| `dataclasses` | Models |
| `os` | Environment and system operations |
| `sys` | Application runtime |
| `tempfile` | Temporary files |
| `urllib` | Basic HTTP functionality, if needed |

---

## 6.2 Development dependencies

| Package | Purpose |
|---|---|
| pytest | Testing |
| textual.testing | TUI testing support | Yes |
| pytest-cov | Coverage |
| Ruff | Linting and formatting |
| mypy | Type checking |

### Optional later

- pre-commit
- tox
- nox

---

## 6.3 External dependencies ToolMate manages

These are not dependencies required to run ToolMate itself.

They are dependencies that ToolMate installs and manages for eSim.

| Dependency | Category |
|---|---|
| KiCad | PCB design |
| Ngspice | Circuit simulation |
| GHDL | VHDL simulation |
| Verilator | HDL simulation |
| Python runtime | eSim runtime |
| Textual | TUI dependency, if used as an extension |
| Matplotlib | Plotting |
| Watchdog | File monitoring |
| Hdlparse | HDL parsing |
| NGHDL components | HDL integration |
| Makerchip components | HDL workflows |

The final list, exact package names, and supported versions must be verified from the targeted eSim release.

---

# 7. requirements.txt

Initial runtime requirements:

```txt
textual
rich
PyYAML
packaging
psutil
requests
platformdirs
```

For the initial development phase, these can be pinned after compatibility testing.

Example future format:

```txt
textual==1.0.0
rich==13.9.4
PyYAML==6.0.2
packaging==25.0
psutil==7.0.0
requests==2.32.4
platformdirs==4.3.8
```

**These example pins are placeholders, not a tested compatibility lock.** We should choose and verify versions in our actual environment before locking.

---

# 8. requirements-dev.txt

```txt
-r requirements.txt

pytest
pytest-cov
ruff
mypy
```

---

# 9. Installation Commands

## Windows

Create virtual environment:

```powershell
python -m venv .venv
```

Activate:

```powershell
.venv\Scripts\activate
```

Install runtime dependencies:

```powershell
pip install -r requirements.txt
```

Install development dependencies:

```powershell
pip install -r requirements-dev.txt
```

---

## Linux

Create virtual environment:

```bash
python3 -m venv .venv
```

Activate:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Some Linux distributions may require system packages for Python virtual environments or terminal rendering support.

---

# 10. Implementation Order of Core Modules

The recommended coding order:

```text
1. models.py
       ↓
2. manifest_manager.py
       ↓
3. system_detector.py
       ↓
4. package_manager_detector.py
       ↓
5. executable_detector.py
       ↓
6. dependency_scanner.py
       ↓
7. compatibility_checker.py
       ↓
8. scan_service.py
       ↓
9. dashboard.py
       ↓
10. workers.py
       ↓
11. installation engine
       ↓
12. verification engine
       ↓
13. Fix All
       ↓
14. diagnostics
       ↓
15. eSim integration
```

Each module must have basic tests before moving on to dependent modules.

---

# 11. First Milestone

## Milestone 1: Working Dependency Scanner

The first version should:

1. Launch ToolMate.
2. Detect operating system.
3. Detect eSim installation path, or allow manual selection.
4. Load dependency manifest.
5. Scan a small set of dependencies.
6. Detect installation status and version.
7. Compare versions against requirements.
8. Display results in a GUI.
9. Allow the user to refresh the scan.

### Initial dependencies for scanner testing

Start with a small sample:

- Python
- Ngspice
- KiCad

Then add more tools after the detection system works reliably.

### Milestone completion criteria

The scanner must correctly distinguish:

- Installed and compatible
- Installed but incompatible
- Missing
- Installed but not detected
- Detection error

**No installations yet.**

Installation is a separate milestone. We must prove detection works before allowing the software to modify a user's machine.

---

# 12. Recommended MVP Build Sequence

| Milestone | Deliverable |
|---|---|
| M1 | Project skeleton |
| M2 | Manifest loader |
| M3 | System detector |
| M4 | Dependency scanner |
| M5 | Compatibility engine |
| M6 | Dashboard |
| M7 | Installation engine |
| M8 | Verification |
| M9 | Fix All |
| M10 | Diagnostics |
| M11 | eSim integration |
| M12 | Packaging and release |

---

# Final Implementation Principle

ToolMate will be developed as a **detection-first, verification-driven system**.

The core engine should remain independent of the GUI and operating system wherever possible. Platform-specific operations will be isolated behind adapters. Dependencies will be defined through a manifest rather than hardcoded into application logic.

The first functional goal is not to install everything.

It is to reliably answer:

**What is installed? What is missing? What is compatible? What is broken?**

Once ToolMate can answer those questions correctly, installation automation becomes a controlled extension of the same system.
