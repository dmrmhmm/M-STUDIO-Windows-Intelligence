"""Safe, bounded PowerShell inventory adapter.

Only fixed read-only commands are permitted. Never pass user-controlled command text.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from typing import Any

_FIXED_COMMAND = (
    "$ErrorActionPreference = 'Stop'; "
    "Get-CimInstance -ClassName Win32_OperatingSystem | "
    "Select-Object Caption, Version, BuildNumber, OSArchitecture | "
    "ConvertTo-Json -Compress"
)


def get_windows_os_details(timeout_seconds: int = 8) -> dict[str, Any] | None:
    """Return a small Windows OS metadata object, or None when unavailable."""
    executable = shutil.which("powershell.exe") or shutil.which("pwsh")
    if executable is None:
        return None
    try:
        completed = subprocess.run(
            [executable, "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", _FIXED_COMMAND],
            capture_output=True,
            text=True,
            timeout=max(1, min(int(timeout_seconds), 15)),
            check=False,
            shell=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0 or not completed.stdout.strip():
        return None
    try:
        data = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None
