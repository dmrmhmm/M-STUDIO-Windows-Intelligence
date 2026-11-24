"""Non-executing maintenance previews."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MaintenancePreview:
    title: str
    reason: str
    proposed_change: str
    risk: str
    requires_confirmation: bool = True
    executable: bool = False


def build_maintenance_preview(title: str, reason: str, proposed_change: str) -> MaintenancePreview:
    """Describe a proposed action; execution is intentionally not implemented."""
    return MaintenancePreview(
        title=title,
        reason=reason,
        proposed_change=proposed_change,
        risk="Not assessed; manual review required.",
    )
