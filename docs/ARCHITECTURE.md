# Architecture

## Layers
1. **UI**: PySide6 presentation only. It receives a snapshot and renders it.
2. **Core**: typed data model and diagnostics orchestration. No UI dependencies.
3. **Adapters**: bounded operating-system integrations. PowerShell is restricted to a fixed CIM read query.
4. **Tests**: portable tests validate the model and core behavior without requiring Windows.

## Data flow
Application startup -> collect read-only snapshot -> construct typed model -> render dashboard.

## Trust boundaries
- No free-form command strings are accepted.
- subprocess calls use argument arrays, `shell=False`, a timeout, and captured output.
- PowerShell is optional. Failure to locate or execute it returns no optional metadata.
- No network client or telemetry exists in this phase.
- The UI cannot invoke system mutations.

## Future extension gate
Any feature that changes the host must be isolated behind a separately reviewed action interface. It must include a preview, explicit consent, privilege explanation, backup/rollback plan, audit record, and tests for cancellation and failure. Never turn a recommendation into an automatic action.
