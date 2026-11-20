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
│ Chocolatey            Pip                   │
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
