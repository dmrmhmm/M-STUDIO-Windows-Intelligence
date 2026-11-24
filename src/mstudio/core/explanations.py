"""Local, deterministic explanations for common system metrics."""
from __future__ import annotations

METRIC_EXPLANATIONS = {
    "cpu_percent": "Approximate share of processor capacity currently in use.",
    "memory_percent": "Percentage of physical memory currently in use.",
    "disk_percent": "Percentage of the selected volume currently occupied.",
    "health_score": "A transparent score based only on available measurements and observed warnings.",
}


def explain_metric(metric_key: str) -> str:
    """Return a local explanation; no network or AI provider is contacted."""
    return METRIC_EXPLANATIONS.get(metric_key, "No explanation is available for this metric.")
