# M / STUDIO Windows Intelligence

A lightweight Windows 10/11 desktop companion for system visibility, diagnostics, and carefully controlled maintenance.

## Current development status
**Phase 0.4 · Intelligence foundations**. The repository includes a command dashboard and read-only foundations for system health, performance, warning diagnosis, hardware and storage inventory, driver/security audits, local AI explanations, reports, and maintenance previews. This remains a development build, not a signed installer or a verified Windows release.

## Safety model
- System inspection and recommendations are read-only; Windows settings, services, registry keys, startup entries, and installed packages are not modified.
- Local JSON reports and SQLite history are written only after the user explicitly chooses a destination.
- No arbitrary shell command input or execution.
- PowerShell calls are fixed, bounded, non-interactive inventory queries.
- Missing permissions or unavailable platform data are reported, not bypassed.
- Recommendations are informational. They never execute actions.
- Future write-capable features require a separate design review, explicit per-action consent, backup/rollback strategy, and tests.

## Features
- Desktop dashboard for OS, CPU, memory, disk, and runtime information.
- Background refresh that keeps the interface responsive and preserves the last valid snapshot on errors.
- Optional Windows edition, version, build, architecture, and processor identification through fixed, read-only CIM queries.
- Cross-platform fallback for development and automated tests.
- Structured diagnostics model with collection timestamps and warnings.
- Transparent health scoring and advisory-only recommendations.
- On-demand performance snapshot, bounded live monitor, and local JSON report export.
- Explicitly enabled local SQLite history with bounded retention (30 days / 1,000 records by default).
- Optional AI explanations through a user-selected Ollama model on loopback only; disabled unless explicitly invoked.
- Read-only driver, Defender/firewall, BIOS, baseboard, and graphics inventory on Windows; serial identifiers are excluded.
- Bounded on-demand inventory of up to 32 accessible mounted volumes; the overview disk metric remains focused on the system volume.
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

## Build a Windows portable package
The `Windows portable package` workflow runs manually, on `v*` tags, and when application or packaging sources change on `main`. It builds a Windows x64 onedir application and publishes a ZIP artifact. This is a portable build, not a signed installer; a real Windows launch smoke test is still required.

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
No API key, cloud account, or administrator permission is required. No telemetry is sent. The optional AI explanation action connects only to `127.0.0.1:11434` after the user selects a local model; it never sends diagnostics to a remote AI service.

## Status and limitations
This is an early foundation, not a system optimizer or repair utility. Metrics depend on the host OS and available permissions. The overview disk metric describes the system volume; a separate on-demand scan lists at most 32 accessible mounted volumes. Windows-specific inventory is optional and reports unavailable when PowerShell or a provider is missing; it does not request elevated permissions. Manual refresh, storage inventory, and Windows system audit run in background workers. Snapshot history is never written by default; the user must choose a local SQLite file, and retention is bounded. Driver and security data are informational snapshots, not update recommendations or a complete security assessment. The optional local AI provider contacts only 127.0.0.1 after explicit user invocation; no remote AI service or telemetry is used.

## License
MIT. See [LICENSE](LICENSE). Third-party notices are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
