"""Read-only system inventory orchestration."""

from __future__ import annotations

import os
import platform

from mstudio.adapters.powershell import get_windows_os_details
from mstudio.core.models import SystemSnapshot


def collect_snapshot() -> SystemSnapshot:
    snapshot = SystemSnapshot(
        operating_system=f"{platform.system()} {platform.release()}".strip(),
        hostname=platform.node() or "Unknown",
        processor=platform.processor() or "Unknown",
    )
    if platform.system() == "Windows":
        windows_details = get_windows_os_details(timeout_seconds=3)
        if windows_details:
            snapshot.os_caption = str(windows_details.get("Caption") or "")
            snapshot.os_version = str(windows_details.get("Version") or "")
            snapshot.os_build = str(windows_details.get("BuildNumber") or "")
            snapshot.os_architecture = str(windows_details.get("OSArchitecture") or "")

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
    except Exception as exc:  # Preserve partial diagnostics for unexpected provider errors.  # noqa: BLE001
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
    except Exception as exc:  # Preserve partial diagnostics for unexpected provider errors.  # noqa: BLE001
        snapshot.warnings.append(f"Disk collection failed: {type(exc).__name__}: {exc}")
    return snapshot
