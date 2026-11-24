"""Read-only system inventory orchestration."""

from __future__ import annotations

import os
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
    except ImportError:
        snapshot.warnings.append("psutil is not installed; resource metrics are unavailable.")
        return snapshot

    snapshot.logical_cores = psutil.cpu_count(logical=True)
    try:
        memory = psutil.virtual_memory()
        snapshot.memory_total_bytes = int(memory.total)
        snapshot.memory_available_bytes = int(memory.available)
        snapshot.memory_percent = float(memory.percent)
    except (OSError, PermissionError) as exc:
        snapshot.warnings.append(f"Memory metrics could not be read: {exc}")
    except Exception as exc:
        snapshot.warnings.append(f"Memory collection failed: {type(exc).__name__}: {exc}")

    try:
        # os.path.abspath(os.sep) resolves to the current system drive on Windows.
        system_root = os.path.abspath(os.sep)
        disk = psutil.disk_usage(system_root)
        snapshot.disk_total_bytes = int(disk.total)
        snapshot.disk_free_bytes = int(disk.free)
        snapshot.disk_percent = float(disk.percent)
    except (OSError, PermissionError) as exc:
        snapshot.warnings.append(f"System disk metrics could not be read: {exc}")
    except Exception as exc:
        snapshot.warnings.append(f"Disk collection failed: {type(exc).__name__}: {exc}")
    return snapshot
