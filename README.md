# ToolMate

ToolMate is a modular desktop dependency management application for eSim.

## Phase 1

The current implementation detects the operating system, OS version, CPU architecture,
available package managers, administrator status, eSim installation location, and relevant
environment variables. It presents this information in a basic PyQt5 window.

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
