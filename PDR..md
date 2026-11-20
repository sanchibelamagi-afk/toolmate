# ToolMate
## Product Design Requirements (PDR)

**Project:** eSim ToolMate  
**Document Version:** 0.1  
**Status:** Draft  
**Product Type:** Terminal Dependency Management Application  
**Target Platform:** Windows 10/11 and Ubuntu/Debian-based Linux (22.04+)  
**User Interface:** Textual TUI with Rich rendering  
**Primary Integration:** eSim EDA Software  

---

## 1. Problem Statement

eSim depends on multiple external software tools, libraries, simulators, and supporting components to perform circuit design, simulation, PCB design, and mixed-signal workflows.

Users currently need to manually install, configure, maintain, and troubleshoot these dependencies. This process can result in:

- Missing dependencies
- Incorrect or incompatible software versions
- Incorrect executable paths
- Configuration errors
- Installation failures
- Difficulty identifying the cause of simulation errors
- Repeated setup effort across systems

These problems increase setup time, create unnecessary frustration, and make eSim harder to use, particularly for new users.

**ToolMate aims to automate dependency detection, compatibility checking, installation, and basic repair for eSim through a centralized, user-friendly interface.**

---

## 2. Product Vision

To create a reliable dependency management system that allows eSim users to check, install, configure, and validate the tools required for their environment with minimal manual effort.

ToolMate should make the process of preparing an eSim environment simple, transparent, and reliable.

### Product principle

> Detect automatically. Explain clearly. Execute safely. Verify everything.

---

## 3. Goals and Objectives

### Primary goals

1. Automatically identify the operating system and system environment.
2. Detect installed dependencies and their versions.
3. Identify missing, outdated, incompatible, and misconfigured dependencies.
4. Compare installed dependencies against a version-controlled compatibility manifest.
5. Install or repair dependencies with explicit user approval.
6. Provide a unified dashboard for dependency health.
7. Verify successful installations and configurations.
8. Generate logs and diagnostic reports for troubleshooting.

### Success criteria

- Users can identify missing dependencies without manually checking each installation.
- Dependency status is clearly visible and understandable.
- Supported missing dependencies can be installed through ToolMate.
- Installed dependencies are verified after installation.
- A failed dependency operation does not unnecessarily prevent other independent operations.
- Users can understand what ToolMate is about to change before approving it.

---

## 4. Target Users

### 4.1 Primary users

**Students and beginners**

Users who install eSim for educational purposes and may not be familiar with package managers, environment variables, dependencies, or software compatibility.

**Electronics and circuit design engineers**

Users who need eSim and its simulation tools configured correctly for their engineering workflow.

**Researchers and educators**

Users working with analog, digital, mixed-signal, and HDL simulation environments.

### 4.2 Secondary users

- eSim developers
- Linux and Windows users managing multiple software versions
- Lab administrators setting up engineering workstations
- Contributors and maintainers of eSim-related tools

---

## 5. Core Features

### F1. System Detection

Automatically detect:

- Operating system
- OS version
- CPU architecture
- Available package manager
- Administrator privileges
- Relevant environment variables
- eSim installation directory
- Existing dependency paths

### F2. Dependency Scanner

Scan the system for supported dependencies.

For every dependency, collect:

- Dependency name
- Installation status
- Installed version
- Installation location
- Detection method
- Compatibility status
- Availability of an installation or repair action

### F3. Compatibility Engine

Compare detected dependency versions and configurations against the approved manifest.

Possible dependency statuses:

| Status | Meaning |
|---|---|
| Installed | Dependency detected and compatible |
| Missing | Dependency not detected |
| Outdated | Installed version is below the supported version |
| Incompatible | Installed version violates compatibility requirements |
| Misconfigured | Dependency exists but configuration/path is invalid |
| Unknown | Version or status could not be determined |
| Checking | Detection is currently running |
| Installing | Installation is in progress |
| Failed | An operation failed |

### F4. Dependency Dashboard

Provide a GUI dashboard showing:

- Overall environment health
- Total dependencies checked
- Installed dependencies
- Missing dependencies
- Incompatible dependencies
- Misconfigured dependencies
- Available actions

Each dependency should have an individual detail view.

### F5. Installation Manager

Install missing dependencies using supported installation sources:

- APT on Linux
- Winget on Windows
- Chocolatey on Windows, where applicable
- Pip for Python packages
- Official vendor installers
- Verified GitHub releases
- Local installation packages

ToolMate must display the intended installation action and request user approval before executing it.

### F6. Fix All

A single **Fix All** action should:

1. Scan the environment.
2. Identify dependencies that can be fixed automatically.
3. Display a summary of planned changes.
4. Request user approval.
5. Execute approved operations in a controlled sequence.
6. Skip dependencies that fail when safe to continue.
7. Verify the resulting environment.
8. Display a final report.

Fix All must never execute silently.

### F7. Verification Engine

After installation or repair, ToolMate must verify the dependency through appropriate checks, such as:

- Executable existence
- Version command
- Installation path
- Required Python import
- Configuration validation
- Basic tool execution or smoke test

A successful installer exit code alone must not be treated as proof that the dependency works.

### F8. Logging and Diagnostics

Maintain logs for:

- System scans
- Version detection
- Installation commands
- User approvals
- Download activity
- Checksum verification
- Installation outcomes
- Configuration changes
- Errors and retries

Provide an option to export a diagnostic report.

### F9. eSim Integration

ToolMate should:

- Detect the eSim installation directory.
- Read relevant eSim configuration.
- Validate configured dependency paths.
- Identify dependencies required by the installed eSim version.
- Be accessible through an eSim option such as **Check Dependencies**.
- Be launchable independently.

---

## 6. User Stories

### US-01: Environment scan

As an eSim user, I want ToolMate to scan my computer so that I can identify the tools available on my system.

**Acceptance criteria:**

- System information is detected.
- Dependency scan starts without requiring manual input.
- Results are displayed clearly.
- Failed detection is reported instead of silently ignored.

### US-02: Identify missing tools

As a user, I want to see missing dependencies so that I know what needs to be installed.

**Acceptance criteria:**

- Missing dependencies are identified.
- Each missing dependency is listed separately.
- Supported installation actions are available.

### US-03: Version compatibility

As a user, I want ToolMate to compare installed versions with supported versions so that I can avoid compatibility issues.

**Acceptance criteria:**

- Installed versions are detected where possible.
- Version requirements are read from the manifest.
- Incompatible versions are clearly flagged.

### US-04: Install dependency

As a user, I want to install a missing dependency through ToolMate so that I do not have to perform the installation manually.

**Acceptance criteria:**

- Installation source is selected.
- Installation plan is displayed.
- User approval is required.
- Installation progress is visible.
- Installation is verified afterward.

### US-05: Fix All

As a user, I want to fix all detected dependency problems with one action so that I can prepare my environment faster.

**Acceptance criteria:**

- Fix All summarizes planned changes.
- User confirms the entire plan.
- Dependencies are processed in a safe order.
- Independent operations can continue after a failure.
- Final status is provided for each operation.

### US-06: Configuration validation

As a user, I want ToolMate to check dependency paths and configuration so that installed tools can be found by eSim.

**Acceptance criteria:**

- Relevant executable paths are validated.
- Incorrect or missing paths are reported.
- Safe corrections can be proposed.
- Configuration changes require approval.

### US-07: Diagnostic report

As a user, I want to export a diagnostic report so that I can share useful troubleshooting information.

**Acceptance criteria:**

- Report contains OS information.
- Report contains dependency status and detected versions.
- Report contains relevant errors.
- Sensitive information is excluded or redacted.

### US-08: Offline scan

As a user, I want ToolMate to scan my environment without internet access so that I can diagnose dependency problems offline.

**Acceptance criteria:**

- Detection works offline.
- Compatibility checks work offline.
- Missing online installation sources are clearly reported.
- Local cached packages can be used when available.

### US-09: Permission management

As a user, I want ToolMate to explain why elevated permissions are needed so that I can make an informed decision.

**Acceptance criteria:**

- Elevation is requested only when required.
- The reason for elevation is displayed.
- User-level installation is preferred when supported.

---

## 7. Functional Requirements

### FR-01: Platform Detection

ToolMate shall detect the supported operating system, version, architecture, and package manager.

### FR-02: Dependency Inventory

ToolMate shall maintain a version-controlled dependency manifest containing supported dependencies and their metadata.

### FR-03: Dependency Detection

ToolMate shall detect the presence and version of each supported dependency.

### FR-04: Compatibility Validation

ToolMate shall compare detected versions and configurations against manifest-defined compatibility rules.

### FR-05: Status Classification

ToolMate shall classify each dependency using the defined status categories.

### FR-06: Installation Planning

ToolMate shall generate an installation plan before executing installation actions.

### FR-07: User Approval

ToolMate shall require explicit user confirmation before installing, updating, removing, or modifying dependencies.

### FR-08: Installation Execution

ToolMate shall execute installation actions using supported installation sources and platform-specific methods.

### FR-09: Download Integrity

ToolMate shall verify downloaded packages using trusted checksum information when available and required by the installation method.

### FR-10: Installation Verification

ToolMate shall verify dependencies after installation using version, path, import, or execution checks.

### FR-11: Error Handling

ToolMate shall report operation failures and attempt safe recovery where possible.

### FR-12: Logging

ToolMate shall maintain timestamped logs of its operations.

### FR-13: Diagnostic Export

ToolMate shall allow users to export diagnostic reports.

### FR-14: Offline Detection

ToolMate shall perform dependency detection and compatibility validation without internet access.

### FR-15: eSim Configuration Validation

ToolMate shall validate dependency paths and configuration against the detected eSim installation.

### FR-16: Fix All

ToolMate shall support batch processing of eligible dependency operations following user approval.

### FR-17: Manifest Versioning

ToolMate shall support versioned manifests so dependency compatibility rules can change independently of application code.

### FR-18: Safe Execution

ToolMate shall avoid executing unverified installation scripts or commands and shall provide transparency about actions performed.

---

## 8. Non-Functional Requirements

### NFR-01: Usability

The interface must be understandable to users with limited technical knowledge.

### NFR-02: Reliability

Dependency detection must not crash the application when an individual dependency is missing or detection fails.

### NFR-03: Safety

ToolMate must not silently install, update, remove, or modify software.

### NFR-04: Security

Downloads must use secure sources and integrity verification wherever supported.

Installation commands must not be constructed from untrusted input.

### NFR-05: Performance

A basic dependency scan should complete within a reasonable time. Slow operations must display progress rather than freeze the interface.

### NFR-06: Maintainability

Dependencies, detection rules, compatibility requirements, and installation strategies should be separated from the core application logic.

### NFR-07: Extensibility

New dependencies should be added primarily through manifest entries and reusable detection/install strategies rather than major rewrites.

### NFR-08: Cross-Platform Support

Platform-specific behavior must be isolated to dedicated OS modules.

### NFR-09: Transparency

Users must be able to inspect what ToolMate detected and what it intends to change.

### NFR-10: Recoverability

Failed operations should not unnecessarily affect unrelated dependencies. Recovery and rollback should be attempted only when the operation supports them safely.

---

## 9. Dependency Manifest Design

The manifest shall be the source of truth for dependency requirements.

It should be version-controlled and structured using JSON or YAML.

### Proposed metadata

Each dependency entry should contain:

- Unique ID
- Name
- Category
- Required status
- Supported operating systems
- Supported eSim releases
- Version constraints
- Detection methods
- Installation sources
- Installation instructions or strategies
- Verification methods
- Configuration requirements
- Checksum information, where applicable
- Dependency relationships

### Example YAML structure

```yaml
manifest_version: 1
esim_version: "2.x"

dependencies:

  - id: ngspice
    name: Ngspice
    category: simulator
    required: true

    platforms:
      windows:
        supported: true
      linux:
        supported: true

    version:
      minimum: null
      recommended: null
      tested: []

    detection:
      method: executable
      command: ngspice
      version_args:
        - "--version"

    installation:
      sources:
        - apt
        - winget
        - official_release

    verification:
      method: version_check

    notes: "Version requirements pending verification"
```

**Important:** The sample is a structural example, not a declaration of actual compatible versions.

The final manifest must be validated against official eSim documentation, release-specific installer scripts, and actual compatibility testing.

---

## 10. Edge Cases

### Detection edge cases

- Dependency installed but not present in PATH.
- Multiple versions installed.
- Version command unavailable.
- Version output format differs across operating systems.
- Dependency installed in a custom directory.
- Dependency executable exists but cannot run.
- Dependency is installed through a different package manager.
- Installation is partially completed.
- Dependency is bundled inside eSim.
- Dependency is installed but incompatible.

### Installation edge cases

- No internet connection.
- Download server unavailable.
- Download interrupted.
- Checksum mismatch.
- Package manager unavailable.
- Package manager locked by another process.
- Installation requires administrator privileges.
- User denies elevation.
- Installer exits with an error.
- Installer reports success but dependency cannot be detected.
- Disk space insufficient.
- Conflicting package versions.
- User cancels installation.
- Existing installation conflicts with the new version.

### Configuration edge cases

- Invalid executable path.
- Missing configuration file.
- Malformed configuration.
- Environment variable not updated.
- Environment variable points to an older installation.
- eSim installation directory cannot be identified.
- Multiple eSim installations detected.

### Fix All edge cases

- One installation fails while others can continue.
- A failed dependency is required by another dependency.
- Dependency installation order is incorrect.
- A dependency changes the system environment.
- System restart is required.
- Installation requires user interaction outside ToolMate.
- A package manager installs an unexpected version.

### Security edge cases

- Download source is unavailable or untrusted.
- Checksum does not match.
- Installer requests unexpected privileges.
- Package metadata is invalid.
- A configuration file contains sensitive information.
- Diagnostic report includes usernames, paths, tokens, or secrets.

ToolMate must never bypass integrity checks simply to complete an installation.

---

## 11. MVP Scope

### Included in MVP

1. Windows 10/11 detection.
2. Ubuntu/Debian-based Linux detection, with the supported baseline defined through testing.
3. System and package manager detection.
4. eSim installation path detection.
5. Dependency manifest loading.
6. Dependency scanning.
7. Version detection.
8. Compatibility validation.
9. Dashboard with dependency status.
10. Individual dependency installation.
11. Fix All with user approval.
12. Basic installation verification.
13. Error handling and logs.
14. Diagnostic report export.
15. Basic offline scanning.
16. Textual terminal dashboard using Rich rendering.

### Excluded from MVP

- macOS support.
- Full CLI.
- Silent automatic updates.
- Automatic updates without approval.
- Advanced rollback.
- Cloud synchronization.
- Remote management.
- AI troubleshooting assistant.
- Automatic dependency discovery from arbitrary software.
- Plugin marketplace.
- Full offline installation bundle.
- Advanced dependency graph visualization.

---

## 12. MVP Workflow

### First launch

1. User launches ToolMate.
2. ToolMate detects OS and environment.
3. ToolMate locates eSim.
4. ToolMate loads the appropriate dependency manifest.
5. ToolMate scans the system.
6. ToolMate compares results against compatibility requirements.
7. Dashboard displays dependency statuses.

### User fixes dependencies

1. User selects Install or Fix All.
2. ToolMate generates an action plan.
3. User reviews the proposed actions.
4. User approves.
5. ToolMate downloads or retrieves packages.
6. Integrity checks are performed.
7. Installation is executed.
8. ToolMate verifies the result.
9. Dashboard refreshes.
10. Logs and final report are updated.

---

## 13. MVP Acceptance Criteria

The MVP will be considered successful when:

- [ ] ToolMate launches on the supported Windows and Linux environments.
- [ ] OS and package manager are detected correctly.
- [ ] eSim installation path can be detected or manually selected.
- [ ] The manifest can be loaded and validated.
- [ ] Supported dependencies can be scanned.
- [ ] Installed versions can be detected where available.
- [ ] Missing and incompatible dependencies are correctly classified.
- [ ] Dashboard displays the dependency status.
- [ ] Installation plans are shown before execution.
- [ ] User approval is required for system changes.
- [ ] At least one supported dependency can be installed successfully through ToolMate on each target platform.
- [ ] Installed dependencies are verified.
- [ ] Failures are logged and displayed clearly.
- [ ] Fix All handles independent failures without unnecessarily aborting the entire operation.
- [ ] Diagnostic reports can be exported.
- [ ] Basic scans and compatibility checks work offline.
- [ ] ToolMate does not silently perform system modifications.

---

## 14. Proposed Development Phases

### Phase 1: Research and Specification

- Research eSim dependencies.
- Analyze official installer scripts.
- Identify OS-specific dependencies.
- Establish compatibility rules.
- Create initial manifest.

### Phase 2: System Detection

- Implement OS detection.
- Detect package managers.
- Detect eSim installation.
- Implement dependency detection strategies.

### Phase 3: Compatibility Engine

- Parse manifest.
- Compare versions.
- Generate dependency statuses.
- Implement dependency relationship handling.

### Phase 4: Textual TUI

- Build Textual terminal dashboard.
- Display dependency statuses.
- Add scan and refresh actions.
- Add dependency detail views.

### Phase 5: Installation Engine

- Implement package manager interfaces.
- Implement approved installation actions.
- Add permission handling.
- Add download integrity checks.

### Phase 6: Verification and Diagnostics

- Verify installed dependencies.
- Implement logs.
- Implement error reporting.
- Export diagnostic reports.

### Phase 7: Integration and Testing

- Integrate with eSim.
- Test on clean Windows and Linux environments.
- Test failure scenarios.
- Validate manifest compatibility.
- Conduct MVP acceptance testing.

---

## 15. Future Enhancements

- CLI interface.
- Offline installation bundles.
- Advanced rollback.
- Automatic update notifications.
- Dependency graph visualization.
- Repair recommendations.
- Multi-version dependency support.
- Additional Linux distributions.
- macOS support.
- Integration with eSim release management.
- Advanced diagnostic analysis.

---

## 16. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Version incompatibility | Release-specific manifest and testing |
| Incorrect dependency detection | Multiple detection strategies |
| Installer failure | Logging, retry policy, safe continuation |
| Privilege escalation | Request elevation only when required |
| Untrusted downloads | Trusted sources and integrity verification |
| Platform differences | OS-specific modules |
| eSim configuration changes | Version-aware detection |
| Partial installation | Post-install verification and recovery guidance |
| Manifest becomes outdated | Version control and validation process |

---

## 17. Definition of Done

A feature is complete when:

1. It meets its defined requirements.
2. It has been tested on supported operating systems.
3. Failure cases have been considered.
4. Errors are handled and logged.
5. User-facing behavior is understandable.
6. System modifications require appropriate confirmation.
7. Documentation is updated.
8. Acceptance criteria are satisfied.

---

## 18. Final Product Summary

ToolMate is a semi-automatic dependency management application for eSim that identifies the user's system environment, detects required software, validates compatibility, and assists with installing or repairing dependencies.

It centralizes a process that currently requires users to manually inspect their system and troubleshoot individual tools.

Its core purpose is not simply to install software. It is to ensure that the eSim environment is **detected, compatible, correctly configured, and verifiable**.

**MVP focus: Detect → Diagnose → Approve → Install → Verify.**
