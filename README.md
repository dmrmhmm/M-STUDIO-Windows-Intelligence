# M / STUDIO Windows Intelligence

A lightweight Windows 10/11 desktop companion for system visibility, diagnostics, and carefully controlled maintenance.

## Current release line
**Phase 0.1 · Foundation**. This repository currently provides a read-only diagnostics desktop application. It does not modify Windows settings, registry keys, services, startup entries, packages, or files.

## Safety model
- Read-only collection is the default and only implemented operating mode.
- No arbitrary shell command input or execution.
- PowerShell calls are fixed, bounded, non-interactive inventory queries.
- Missing permissions or unavailable platform data are reported, not bypassed.
- Recommendations are informational. They never execute actions.
- Future write-capable features require a separate design review, explicit per-action consent, backup/rollback strategy, and tests.

## Features
- Desktop dashboard for OS, CPU, memory, disk, and runtime information.
- Cross-platform fallback for development and automated tests.
- Structured diagnostics model with collection timestamps and warnings.
- Small modular architecture suitable for low-resource Windows PCs.

## Requirements
- Windows 10/11 (x64) for the intended desktop experience.
- Python 3.11 or newer.
- PySide6 for the desktop UI.
- psutil for process-independent system metrics.

## Quick start (Windows PowerShell)
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m mstudio
```

If script activation is restricted, run the venv interpreter directly:
```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m mstudio
```

## Run tests
```powershell
python -m pytest
```

## Project layout
- `src/mstudio/core`: domain models and diagnostics orchestration.
- `src/mstudio/adapters`: operating-system data providers.
- `src/mstudio/ui`: PySide6 desktop interface.
- `tests`: unit tests that do not require Windows.
- `docs`: architecture, roadmap, and security notes.

## Configuration
No API key, cloud account, or administrator permission is required. No telemetry is sent. The initial version does not connect to a remote AI service.

## Status and limitations
This is an early foundation, not a system optimizer or repair utility. Metrics depend on the host OS and available permissions. Disk usage is reported for the current system volume only. Windows-specific CIM details are optional and gracefully fall back when PowerShell is unavailable.

## License
MIT. See [LICENSE](LICENSE). Third-party notices are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
