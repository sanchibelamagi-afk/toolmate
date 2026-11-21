# ToolMate

ToolMate is a Textual-based terminal application for inspecting eSim dependency health on
Windows and Linux. It detects the system, scans dependencies from the manifest, compares
versions with compatibility rules, and requires confirmation before running installation
commands.

## Requirements

- Python 3.10 or later
- Windows 10/11 or Ubuntu/Debian-based Linux

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
- `x`: request safe cancellation of a running installation or download
- `/`: focus dependency filtering
- `q`: quit

The dashboard includes system details, resource information, dependency status counts,
search/filter, package details, and live installation output. Download sources require a
manifest-provided SHA-256 checksum. Installers are never launched automatically after a
download. Batch installation lists the commands before approval, reports individual
failures, continues with independent operations, and rescans when the batch finishes.

Windows package metadata currently uses the verified Winget IDs `Python.Python.3.14` and
`KiCad.KiCad`. Ngspice is not present in the default Winget source; its manifest specifies
Chocolatey package `ngspice` and links to the [official download instructions](https://ngspice.sourceforge.io/download.html)
for portable/manual setup.

## Tests and lint

```powershell
python -m pytest tests/unit -q
ruff check main.py src tests
```

## Configuration

Dependency definitions and install-source metadata are maintained in `config/manifest.yaml`.
Version compatibility rules live alongside each dependency; source-specific package IDs are
not inferred from dependency names.
