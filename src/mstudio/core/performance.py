"""Lightweight, on-demand performance sampling."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime


@dataclass(frozen=True, slots=True)
class PerformanceSample:
    collected_at: str
    cpu_percent: float | None
    memory_percent: float | None
    disk_percent: float | None


def collect_performance_sample() -> PerformanceSample:
    """Collect one non-blocking sample; does not start a background monitor."""
    try:
        import psutil
    except ImportError:
        return PerformanceSample(datetime.now(UTC).isoformat(timespec="seconds"), None, None, None)
    cpu = float(psutil.cpu_percent(interval=None))
    try:
        memory = float(psutil.virtual_memory().percent)
    except (OSError, PermissionError):
        memory = None
    try:
        import os
        disk = float(psutil.disk_usage(os.path.abspath(os.sep)).percent)
    except (OSError, PermissionError):
        disk = None
    return PerformanceSample(
        datetime.now(UTC).isoformat(timespec="seconds"), cpu, memory, disk
    )


def sample_to_dict(sample: PerformanceSample) -> dict[str, object]:
    return asdict(sample)
