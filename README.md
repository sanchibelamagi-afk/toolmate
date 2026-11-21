# ToolMate

ToolMate is a Textual-based terminal application for inspecting and maintaining eSim
dependencies on Windows, Linux, and macOS. It detects the system, scans dependencies from
the manifest, compares versions with compatibility rules, and requires confirmation
before installing or updating tools or changing the user's environment.

## Requirements

- Python 3.10 or later
- Windows 10/11, Ubuntu/Debian- or Arch-based Linux, or macOS with Homebrew

## Install for development

From the project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m pip install -r requirements-dev.txt
```

Editable installation creates the `toolmate` command in the active environment.

On Linux or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m pip install -r requirements-dev.txt
```

## Run

```powershell
toolmate
```

Alternatively, run from the project directory:

```powershell
python main.py
```

## TUI controls

- `s`: scan or refresh system information and dependencies
- `i`: show the install plan and confirmation prompt for the selected dependency
- `u`: check for available updates, display them in the table, and confirm an update
  for the selected tool
- `b`: review and install all missing dependencies with supported automated package
  managers after one confirmation
- `c`: preview or configure the detected eSim environment and tool PATH entries
- `m`: toggle Safe Mode; the current state appears in the header and footer
- `x`: request safe cancellation of a running installation, update, or download
- `/`: focus dependency filtering
- `q`: quit

With Safe Mode ON, `i`, `b`, and `u` preview and log commands without running them.
`c` previews environment changes without writing them. Turn Safe Mode OFF and explicitly
approve a confirmation modal to make system changes.

The dashboard includes system details, resource information, dependency status counts,
search/filter, package details, and live installation output. Download sources require a
manifest-provided SHA-256 checksum. Installers are never launched automatically after a
download. Batch installation lists the commands before approval, reports individual
failures, continues with independent operations, and rescans when the batch finishes.
Scans, command previews, installer output, installation outcomes, and errors are recorded
in `logs/toolmate.log`; generated log files are ignored by Git.

## eSim toolchain

The manifest tracks 12 tools. Detection uses version commands for executables and
platform-specific directory checks for PDK/source checkouts.

| Tool | Windows package mappings | Linux package mappings | macOS/Homebrew |
|---|---|---|---|
| Python | Winget `Python.Python.3.14` | APT `python3`; pacman `python` | `python@3.14` |
| Git | Winget `Git.Git`; Chocolatey `git` | APT/pacman `git` | `git` |
| KiCad | Winget `KiCad.KiCad` | APT/pacman `kicad` | Manual official installer |
| Ngspice | Chocolatey `ngspice` | APT/pacman `ngspice` | `ngspice` |
| GHDL | Winget `ghdl.ghdl.ucrt64.mcode` | APT `ghdl` | No verified formula; use official instructions |
| OpenModelica | Winget `OpenModelica.OpenModelica.Official` | APT `openmodelica` (official repository required) | Official installer |
| Verilator | No verified Winget/Chocolatey package | APT/pacman `verilator` | `verilator` |
| Icarus Verilog | Winget `Icarus.Verilog`; Chocolatey `iverilog` | APT/pacman `iverilog` | `icarus-verilog` |
| Makerchip | Browser-based service; no local package | Browser-based service; no local package | Browser-based service |
| OpenROAD Flow | Unsupported | Manual source checkout; detected by path | Unsupported |
| SkyWater SKY130 PDK | Not supported natively | Detected under `PDK_ROOT/sky130A` or common PDK paths | Not supported natively |
| IHP PDK | Not supported natively | Detected under `PDK_ROOT/ihp-sg13g2` or common PDK paths | Not supported natively |

Tools without a verified package mapping provide official setup guidance in the manifest.
Makerchip availability cannot be detected locally; it is reported as an external service,
not as a missing executable.

Update checks use Winget, APT, pacman, or Homebrew's read-only outdated listing. Use `[u]`
to check versions; available updates are shown in the table, and the selected upgrade
still requires confirmation. Homebrew is detected automatically on macOS and is used for
manifest-mapped formulas.

`[c] Configure Env` prepares `ESIM_HOME` and detected executable directories. Safe Mode
shows the proposed changes without writing. Otherwise, a confirmation is required and a
backup is created first: Windows updates only the current user's Environment registry
values, Linux uses `~/.profile`, and macOS uses `~/.zprofile`. Open a new terminal after
applying the changes. Existing ToolMate-managed profile entries are replaced rather than
duplicated; backups are saved under `~/.toolmate/backups`.

## eSim integration

Launch ToolMate from an eSim menu or launcher while passing the eSim installation
directory:

```powershell
toolmate --esim-path "C:\Program Files\eSim"
```

```bash
toolmate --esim-path "$HOME/esim"
```

For a non-interactive compatibility report, eSim can invoke:

```powershell
toolmate --check-dependencies --esim-path "C:\Program Files\eSim" `
  --dependency-path "ngspice=C:\tools\ngspice\bin\ngspice.exe"
```

```bash
toolmate --check-dependencies --esim-path "$HOME/esim" \
  --dependency-path "ngspice=/usr/bin/ngspice"
```

The command writes a JSON report to stdout with system information, dependency
compatibility, detected executable paths, eSim-root validation, and any supplied
eSim-configured dependency-path checks. Repeat `--dependency-path ID=PATH` for each
configured tool. A missing configured path is reported as `exists: false`; an unknown
dependency ID or invalid explicit eSim root returns a JSON error and nonzero exit code.

An eSim-side **Check Dependencies** menu item can call this command and parse stdout,
while a **Launch ToolMate** item can run `toolmate --esim-path <eSim-directory>`. This
repository provides the integration interface; the eSim application source itself is
maintained separately.

## Packaging and releases

The package version in `pyproject.toml` is the release version source. Build a wheel and
source archive locally with:

```powershell
python -m pip install -r requirements-dev.txt
python -m build --outdir dist
```

The GitHub Actions workflow runs tests and Ruff on Windows, Linux, and macOS, then builds
installable wheel and source-distribution artifacts on each operating system. Install a
downloaded wheel with `python -m pip install <wheel-file>`; its declared dependencies are
installed by pip. For a release, set the version in `pyproject.toml`, create the matching
`v<version>` tag, and attach the workflow's build artifacts to the GitHub release.

### Standalone Windows executable

On Windows, install the development requirements and build the console app as a
self-contained, one-file executable. The PyInstaller spec bundles the canonical manifest:

```powershell
python -m pip install -r requirements-dev.txt
python -m PyInstaller --clean --noconfirm toolmate.spec
.\dist\toolmate.exe --check-dependencies
```

The executable includes its Python runtime and dependencies; target PCs do not need
Python installed. The build writes `dist\toolmate.exe`, while PyInstaller's temporary
files go into `build\`. Both output directories are ignored by Git.

## Screenshot and demo

For a readable capture, use a terminal at least 120 columns wide and 40 rows high, run
`toolmate`, wait for the scan to finish, and show the dependency table with Safe Mode
visible. On Windows, use **Win+Shift+S** to capture the terminal. On Linux, use the
desktop's screenshot shortcut or screenshot utility to capture the terminal window.
For a short demo, record the terminal with your desktop's screen recorder (or a terminal
recorder such as `asciinema` where available), then demonstrate `s` to rescan, `m` to
toggle Safe Mode, `i` for a selected-tool preview, and `b` for a batch preview.

## Tests and lint

```powershell
python -m pytest tests/unit -q
ruff check main.py src tests
```

## Configuration

Dependency definitions and install-source metadata are maintained in `config/manifest.yaml`.
Version compatibility rules live alongside each dependency; source-specific package IDs are
not inferred from dependency names.

## Requirements Compliance

- [x] Manifest-driven inventory for the 12-tool eSim stack on supported platforms.
- [x] Windows Winget/Chocolatey, Linux APT/pacman, and macOS Homebrew adapters.
- [x] Available-update checks and the confirmation-gated `[u] Update` action.
- [x] Safe Mode previews for install, batch install, update, and environment configuration.
- [x] `[c] Configure Env` exports detected tool paths and `ESIM_HOME` to the user environment.
- [x] Backups and stale-change protection before modifying a profile or Windows User PATH.
- [x] Automated Windows/Linux/macOS tests, lint, and package builds in CI.
