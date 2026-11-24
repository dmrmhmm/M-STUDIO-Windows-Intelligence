# Roadmap

## Phase 0.1 - Foundation
- [x] Repository structure and packaging.
- [x] Read-only cross-platform system snapshot.
- [x] Minimal PySide6 dashboard.
- [x] Safe fixed PowerShell CIM adapter.
- [x] Portable unit tests and CI workflow.

## Phase 0.2 - Reliability
- [ ] Windows 10 and Windows 11 smoke tests.
- [ ] Add structured logging with local opt-in.
- [x] Add manual refresh action and update collection timestamp.
- [x] Run startup and refresh collection on a bounded Qt worker thread.
- [x] Keep the last valid dashboard visible when refresh fails.
- [x] Expose stable widget identifiers for UI-level tests.
- [x] Collect optional Windows edition, version, build, and architecture.
- [x] Fall back to a fixed CIM query when the processor name is unavailable.
- [x] Add bounded read-only inventory for up to 32 mounted disk volumes.
- [ ] Add user-selectable volume focus and SMART health where safely available.
- [ ] Add accessibility and high-DPI review.
- [ ] Verify all refresh and metadata behavior in Windows and Ubuntu CI.

## Phase 0.3 - Intelligence foundations
- [x] Add transparent system health scoring from available snapshot metrics.
- [x] Show the health score and status on the dashboard.
- [x] Add rule-based recommendations and conservative warning classification.
- [x] Add non-blocking, on-demand performance sampling foundation.
- [x] Add local JSON report generation foundation (only on explicit invocation).
- [x] Add non-executing maintenance preview contract.
- [x] Add local metric explanations as dashboard tooltips.
- [ ] Add recommendation detail views.
- [ ] Add optional local-only history with retention controls.

## Phase 0.4 - Ten intelligence modules
- [x] 1. System health engine foundation.
- [x] 2. Performance sampling foundation; live chart and bounded polling remain.
- [x] 3. Rule-based warning diagnosis foundation; Windows Event Log analysis remains.
- [x] 4. Hardware intelligence foundation via OS and processor snapshot.
- [x] 5. Bounded mounted-volume storage inventory; volume explorer and SMART remain.
- [x] 6. Read-only Windows driver inventory foundation; update comparison remains.
- [x] 7. Read-only Windows Defender/firewall status audit foundation; privacy review remains.
- [ ] 8. Optional AI explanation provider; local-first, explicit opt-in, no telemetry.
- [x] 9. Local JSON report generation foundation.
- [x] 10. Maintenance preview contract; no action execution.

## Later, subject to explicit review
- [ ] Per-action consent and audit trail.
- [ ] Rollback design for any future approved maintenance action.
- [ ] No unattended or silent system modifications.
