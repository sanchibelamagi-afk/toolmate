# Copilot Working Instructions

- Always read and follow `docs/ARCHITECHURE.md` for architectural and implementation constraints.
- Always read `docs/phases.md` and work only on the tasks belonging to the active phase.
- Do not implement features from future phases.
- Keep GUI code separate from core detection logic.
- Never execute system-changing commands directly from GUI widgets.
- Use platform-specific modules for Windows and Linux behavior.
- Keep the manifest as the source of dependency requirements; do not hardcode dependency requirements in scanners.
- Add or update tests for behavior introduced by the active phase.
- Preserve existing behavior and do not modify unrelated eSim files.
- When a PDR or architecture document has a filename variant or typo, resolve it from the workspace and follow the intended document.
