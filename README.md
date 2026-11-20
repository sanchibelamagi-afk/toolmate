# ToolMate

ToolMate is a modular Terminal UI and CLI dependency management application for eSim.

## Phase 1

The current implementation detects the operating system, OS version, CPU architecture,
available package managers, administrator status, eSim installation location, and relevant
environment variables. It presents this information in a Textual terminal dashboard.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
python main.py
```

## Test

```powershell
python -m pytest tests/unit
```

## Dependency inventory

```powershell
python -c "from src.toolmate.services.scan_service import ScanService; print([(e.id, e.status, len(e.installations)) for e in ScanService('config/manifest.yaml').scan()])"
```

## Launch dashboard

```powershell
python main.py
```

The dashboard shows system information, dependency compatibility, dependency details,
live scan status, and recent log output.
