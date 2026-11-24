# Architecture

## Layers
1. **UI**: PySide6 presentation. It renders typed snapshots and runs refresh collection on Qt's shared thread pool so slow providers do not block the interface.
2. **Core**: typed data model and diagnostics orchestration. No UI dependencies.
3. **Adapters**: bounded operating-system integrations. PowerShell is restricted to fixed CIM read queries for OS and processor metadata.
4. **Tests**: portable tests validate the model, adapters, refresh lifecycle, and core behavior on Windows and Ubuntu.

## Data flow
Application startup -> collect read-only snapshot -> construct typed model -> render dashboard.
Manual refresh -> bounded worker -> read-only provider -> queued Qt signal -> update dashboard on the UI thread.

## Trust boundaries
- No free-form command strings are accepted.
- subprocess calls use argument arrays, `shell=False`, a bounded timeout, and captured output.
- PowerShell is optional. Failure to locate or execute it returns no optional metadata.
- Windows CIM queries are fixed and read-only; no user-supplied query fragments are accepted.
- Refresh failures preserve the last valid dashboard snapshot and display a warning.
- No network client or telemetry exists in this phase.
- The UI cannot invoke system mutations.

## Future extension gate
Any feature that changes the host must be isolated behind a separately reviewed action interface. It must include a preview, explicit consent, privilege explanation, backup/rollback plan, audit record, and tests for cancellation and failure. Never turn a recommendation into an automatic action.
