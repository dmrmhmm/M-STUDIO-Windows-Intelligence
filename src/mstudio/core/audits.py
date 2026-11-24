"""Read-only driver and security audits with explicit availability reporting."""
from __future__ import annotations

import platform
from typing import Any

from mstudio.adapters.powershell import (
    get_windows_driver_inventory,
    get_windows_security_status,
)


def audit_drivers() -> dict[str, Any]:
    if platform.system() != "Windows":
        return {"available": False, "reason": "Driver inventory is currently Windows-only.", "drivers": []}
    drivers = get_windows_driver_inventory(timeout_seconds=10)
    if drivers is None:
        return {"available": False, "reason": "Windows driver inventory could not be read.", "drivers": []}
    return {"available": True, "count": len(drivers), "drivers": drivers}


def audit_security() -> dict[str, Any]:
    if platform.system() != "Windows":
        return {"available": False, "reason": "Security provider is currently Windows-only."}
    status = get_windows_security_status(timeout_seconds=10)
    if status is None:
        return {"available": False, "reason": "Defender/firewall status is unavailable on this system."}
    return {"available": True, "status": status}
