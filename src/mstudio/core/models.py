"""Typed, serialization-friendly diagnostics models."""

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(slots=True)
class Metric:
    label: str
    value: str
    detail: str = ""


@dataclass(slots=True)
class SystemSnapshot:
    collected_at: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat(timespec="seconds")
    )
    operating_system: str = "Unknown"
    os_caption: str = ""
    os_version: str = ""
    os_build: str = ""
    os_architecture: str = ""
    hostname: str = "Unknown"
    processor: str = "Unknown"
    logical_cores: int | None = None
    memory_total_bytes: int | None = None
    memory_available_bytes: int | None = None
    memory_percent: float | None = None
    disk_total_bytes: int | None = None
    disk_free_bytes: int | None = None
    disk_percent: float | None = None
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
