"""Read-only system inventory orchestration."""

from __future__ import annotations

import platform

from mstudio.core.models import SystemSnapshot


def collect_snapshot() -> SystemSnapshot:
    snapshot = SystemSnapshot(
        operating_system=f"{platform.system()} {platform.release()}".strip(),
        hostname=platform.node() or "Unknown",
        processor=platform.processor() or "Unknown",
    )
    try:
        import psutil

        snapshot.logical_cores = psutil.cpu_count(logical=True)
        memory = psutil.virtual_memory()
        snapshot.memory_total_bytes = int(memory.total)
        snapshot.memory_available_bytes = int(memory.available)
        snapshot.memory_percent = float(memory.percent)
        disk = psutil.disk_usage("/")
        snapshot.disk_total_bytes = int(disk.total)
        snapshot.disk_free_bytes = int(disk.free)
        snapshot.disk_percent = float(disk.percent)
    except ImportError:
        snapshot.warnings.append("psutil is not installed; resource metrics are unavailable.")
    except (OSError, PermissionError) as exc:
        snapshot.warnings.append(f"Some resource metrics could not be read: {exc}")
    except Exception as exc:  # Keep diagnostics resilient to platform-specific failures.
        snapshot.warnings.append(f"Resource collection was incomplete: {type(exc).__name__}: {exc}")
    return snapshot
