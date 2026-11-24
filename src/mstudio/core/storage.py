"""Bounded, read-only disk volume inventory."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class StorageVolume:
    mountpoint: str
    filesystem: str
    total_bytes: int
    used_bytes: int
    free_bytes: int
    percent_used: float


def collect_storage_volumes(max_volumes: int = 32) -> list[StorageVolume]:
    """Collect metadata for mounted local volumes, skipping inaccessible entries."""
    try:
        import psutil
    except ImportError:
        return []

    limit = max(1, min(int(max_volumes), 32))
    volumes: list[StorageVolume] = []
    seen: set[str] = set()
    try:
        partitions = psutil.disk_partitions(all=False)
    except (OSError, PermissionError):
        return []

    for partition in partitions:
        mountpoint = str(partition.mountpoint)
        if mountpoint in seen:
            continue
        seen.add(mountpoint)
        try:
            usage = psutil.disk_usage(mountpoint)
        except (OSError, PermissionError):
            continue
        volumes.append(StorageVolume(
            mountpoint=mountpoint,
            filesystem=str(partition.fstype or "Unknown"),
            total_bytes=int(usage.total),
            used_bytes=int(usage.used),
            free_bytes=int(usage.free),
            percent_used=float(usage.percent),
        ))
        if len(volumes) >= limit:
            break
    return volumes


def storage_to_dict(volume: StorageVolume) -> dict[str, Any]:
    return asdict(volume)
