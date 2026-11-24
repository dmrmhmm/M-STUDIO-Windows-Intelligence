"""Deterministic, explainable health scoring and diagnostic recommendations."""
from __future__ import annotations

from dataclasses import dataclass

from mstudio.core.models import SystemSnapshot


@dataclass(frozen=True, slots=True)
class HealthAssessment:
    score: int
    status: str
    findings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Recommendation:
    title: str
    explanation: str
    priority: str
    action: str = "Review only; M / STUDIO does not change system settings."


def assess_health(snapshot: SystemSnapshot) -> HealthAssessment:
    """Calculate a transparent score from available measurements only."""
    score = 100
    findings: list[str] = []
    if snapshot.memory_percent is not None and snapshot.memory_percent >= 90:
        score -= 25
        findings.append("Memory pressure is high (90% or more in use).")
    elif snapshot.memory_percent is not None and snapshot.memory_percent >= 80:
        score -= 12
        findings.append("Memory usage is elevated (80% or more in use).")
    if snapshot.disk_percent is not None and snapshot.disk_percent >= 95:
        score -= 30
        findings.append("System disk is critically full (95% or more used).")
    elif snapshot.disk_percent is not None and snapshot.disk_percent >= 85:
        score -= 15
        findings.append("System disk space is running low (85% or more used).")
    if snapshot.warnings:
        score -= min(20, len(snapshot.warnings) * 5)
        findings.append(f"{len(snapshot.warnings)} diagnostic warning(s) need review.")
    score = max(0, min(100, score))
    status = "Critical" if score < 50 else "Needs attention" if score < 80 else "Healthy"
    return HealthAssessment(score=score, status=status, findings=tuple(findings))


def build_recommendations(snapshot: SystemSnapshot) -> list[Recommendation]:
    """Return conservative recommendations; never execute remediation."""
    items: list[Recommendation] = []
    if snapshot.memory_percent is not None and snapshot.memory_percent >= 80:
        items.append(Recommendation(
            "Review memory usage",
            "Memory pressure is elevated. Review the applications currently using memory.",
            "High" if snapshot.memory_percent >= 90 else "Medium",
        ))
    if snapshot.disk_percent is not None and snapshot.disk_percent >= 85:
        items.append(Recommendation(
            "Review system disk space",
            "Storage usage is high. Inspect large files before deciding what, if anything, to remove.",
            "High" if snapshot.disk_percent >= 95 else "Medium",
        ))
    for warning in snapshot.warnings:
        items.append(Recommendation(
            "Investigate a diagnostic warning", warning, "Medium"
        ))
    if not items:
        items.append(Recommendation(
            "No immediate action suggested",
            "Available measurements do not currently cross M / STUDIO warning thresholds.",
            "Info",
        ))
    return items


def diagnose_warnings(snapshot: SystemSnapshot) -> list[dict[str, str]]:
    """Classify collected warnings without claiming a root cause that is not known."""
    results = []
    for warning in snapshot.warnings:
        lowered = warning.lower()
        category = "system inventory"
        if "memory" in lowered:
            category = "memory"
        elif "disk" in lowered or "storage" in lowered:
            category = "storage"
        results.append({
            "category": category,
            "message": warning,
            "certainty": "Observed warning; root cause not established.",
        })
    return results
