"""User-invoked, local JSON diagnostics report export."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mstudio.core.insights import assess_health, build_recommendations, diagnose_warnings
from mstudio.core.models import SystemSnapshot


def build_report(snapshot: SystemSnapshot) -> dict[str, Any]:
    health = assess_health(snapshot)
    return {
        "report_version": 1,
        "application": "M / STUDIO Windows Intelligence",
        "snapshot": snapshot.to_dict(),
        "health": {
            "score": health.score,
            "status": health.status,
            "findings": list(health.findings),
        },
        "recommendations": [
            {
                "title": item.title,
                "explanation": item.explanation,
                "priority": item.priority,
                "action": item.action,
            }
            for item in build_recommendations(snapshot)
        ],
        "diagnoses": diagnose_warnings(snapshot),
    }


def export_json_report(snapshot: SystemSnapshot, destination: str | Path) -> Path:
    """Write only when explicitly called by the user-facing export action."""
    path = Path(destination)
    path.write_text(
        json.dumps(build_report(snapshot), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path
