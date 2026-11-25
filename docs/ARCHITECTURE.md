# Architecture

## Layers

1. **UI**: PySide6 command dashboard. Startup and refresh collection, Windows system audits, mounted-volume inventory, and local AI explanations use bounded Qt workers so slow providers do not block the interface.
2. **Core**: typed snapshots, transparent health scoring, advisory recommendations, warning classification, performance sampling, local reports, bounded SQLite history, and non-executing maintenance previews.
3. **Adapters**: cross-platform metrics through `psutil`; optional Windows inventory through fixed PowerShell commands.
4. **Tests**: portable unit and UI tests run on Windows and Ubuntu with Python 3.11 and 3.12.

## Data flow

- Startup renders a lightweight placeholder, starts bounded read-only collection, then updates the dashboard through a queued Qt signal.
- Manual refresh collects a new snapshot in a worker and preserves the last valid view if collection fails.
- System audit gathers bounded driver, Defender/firewall, BIOS, baseboard, and graphics metadata in a worker.
- Storage scan inspects at most 32 accessible mounted volumes in a worker.
- Performance sampling is on-demand; the live dialog has a fixed sample limit.
- Local AI explanations run only after the user explicitly selects an installed Ollama model and use the loopback endpoint.
- JSON report export and SQLite history writes occur only after the user explicitly selects a local destination.

## Trust boundaries

- No free-form command strings or user-supplied PowerShell fragments are accepted.
- PowerShell invocations use argument arrays, `shell=False`, non-interactive flags, captured output, and a timeout capped at 15 seconds.
- PowerShell commands are fixed, read-only inventory queries for OS and processor metadata, up to 100 signed-driver rows, Defender/firewall status, and bounded BIOS/baseboard/graphics metadata. No serial identifiers are requested.
- Missing permissions or unavailable platform data are reported as unavailable; the application does not elevate privileges or bypass access controls.
- The optional local AI client targets only `127.0.0.1:11434`, rejects redirects, bounds its timeout and response size, and is disabled unless explicitly invoked. No remote AI endpoint or telemetry is used.
- Reports and history are stored locally only at a destination chosen by the user. No background persistence is enabled by default.
- Recommendations are informational. The UI cannot invoke system mutations, and maintenance previews are not executable.

## Future extension gate

Any feature that changes the host must be isolated behind a separately reviewed action interface. It must include a preview, explicit per-action consent, privilege explanation, backup/rollback plan, audit record, and tests for cancellation and failure. Never turn a recommendation into an automatic action.
