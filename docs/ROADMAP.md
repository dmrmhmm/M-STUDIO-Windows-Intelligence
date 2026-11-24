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
- [ ] Add disk-volume selection with safe defaults.
- [ ] Add accessibility and high-DPI review.
- [ ] Verify all refresh and metadata behavior in Windows and Ubuntu CI.

## Phase 0.3 - Insight
- [ ] Explain metrics in plain language.
- [ ] Add transparent, rule-based recommendations.
- [ ] Export a user-requested diagnostics report.
- [ ] Add optional local-only history with retention controls.

## Later, subject to explicit review
- [ ] Maintenance previews and rollback design.
- [ ] Per-action consent and audit trail.
- [ ] No unattended or silent system modifications.
