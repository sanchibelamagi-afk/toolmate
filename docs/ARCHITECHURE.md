┌─────────────────────────────────────────────┐
│              TOOLMATE GUI                  │
│                 PyQt5                      │
│                                             │
│  Dashboard │ Dependency Status │ Logs       │
│  Install   │ Fix All           │ Settings   │
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