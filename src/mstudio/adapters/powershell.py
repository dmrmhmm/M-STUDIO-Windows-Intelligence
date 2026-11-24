"""Safe, bounded PowerShell inventory adapter.

Only fixed read-only commands are permitted. Never pass user-controlled command text.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from typing import Any

_OS_COMMAND = (
    "$ErrorActionPreference = 'Stop'; "
    "Get-CimInstance -ClassName Win32_OperatingSystem | "
    "Select-Object Caption, Version, BuildNumber, OSArchitecture | "
    "ConvertTo-Json -Compress"
)
_PROCESSOR_COMMAND = (
    "$ErrorActionPreference = 'Stop'; "
    "Get-CimInstance -ClassName Win32_Processor | "
    "Select-Object -First 1 -ExpandProperty Name | ConvertTo-Json -Compress"
)


def _run_fixed_query(command: str, timeout_seconds: int) -> Any | None:
    executable = shutil.which("powershell.exe") or shutil.which("pwsh")
    if executable is None:
        return None
    try:
        completed = subprocess.run(
            [executable, "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", command],
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
        return json.loads(completed.stdout)
    except json.JSONDecodeError:
        return None


def get_windows_os_details(timeout_seconds: int = 8) -> dict[str, Any] | None:
    """Return a small Windows OS metadata object, or None when unavailable."""
    data = _run_fixed_query(_OS_COMMAND, timeout_seconds)
    return data if isinstance(data, dict) else None


def get_windows_processor_name(timeout_seconds: int = 3) -> str | None:
    """Return the first processor model name using a fixed, read-only CIM query."""
    data = _run_fixed_query(_PROCESSOR_COMMAND, timeout_seconds)
    return data.strip() if isinstance(data, str) and data.strip() else None
