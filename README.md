# ToolMate

ToolMate is a Textual-based terminal application for inspecting eSim dependency health on
Windows and Linux. It detects the system, scans dependencies from the manifest, compares
versions with compatibility rules, and requires confirmation before running installation
commands.

## Requirements

- Python 3.10 or later
- Windows 10/11 or Ubuntu/Debian- and Arch-based Linux

## Install for development

From the project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m pip install -r requirements-dev.txt
```

Editable installation creates the `toolmate` command in the active environment.

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
- `b`: review and install all missing dependencies with supported automated package
  managers after one confirmation
- `m`: toggle Safe Mode; the current state appears in the header and footer
- `x`: request safe cancellation of a running installation or download
- `/`: focus dependency filtering
- `q`: quit

With Safe Mode ON, `i` and `b` show and log their planned commands but do not run
installers. Turn Safe Mode OFF and explicitly approve an install plan to make changes.

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

| Tool | Windows package mappings | Linux package mappings |
|---|---|---|
| Python | Winget `Python.Python.3.14` | APT `python3`; pacman `python` |
| Git | Winget `Git.Git`; Chocolatey `git` | APT/pacman `git` |
| KiCad | Winget `KiCad.KiCad` | APT/pacman `kicad` |
| Ngspice | Chocolatey `ngspice` | APT/pacman `ngspice` |
| GHDL | Winget `ghdl.ghdl.ucrt64.mcode` | APT `ghdl` |
| OpenModelica | Winget `OpenModelica.OpenModelica.Official` | APT `openmodelica` (official repository required) |
| Verilator | No verified Winget/Chocolatey package | APT/pacman `verilator` |
| Icarus Verilog | Winget `Icarus.Verilog`; Chocolatey `iverilog` | APT/pacman `iverilog` |
| Makerchip | Browser-based service; no local package | Browser-based service; no local package |
| OpenROAD Flow | Manual source checkout | Manual source checkout; detected by path |
| SkyWater SKY130 PDK | Not supported natively | Detected under `PDK_ROOT/sky130A` or common PDK paths |
| IHP PDK | Not supported natively | Detected under `PDK_ROOT/ihp-sg13g2` or common PDK paths |

Tools without a verified package mapping provide official setup guidance in the manifest.
Makerchip availability cannot be detected locally; it is reported as an external service,
not as a missing executable.

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

The GitHub Actions workflow runs tests and Ruff on Windows and Linux, then builds
installable wheel and source-distribution artifacts on both operating systems. Install a
downloaded wheel with `python -m pip install <wheel-file>`; its declared dependencies are
installed by pip. For a release, set the version in `pyproject.toml`, create the matching
`v<version>` tag, and attach the workflow's build artifacts to the GitHub release.

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
