"""Explicitly enabled, local-only diagnostics history."""
from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path

from mstudio.core.models import SystemSnapshot


def save_snapshot_history(
    snapshot: SystemSnapshot, destination: str | Path, *,
    retention_days: int = 30, max_entries: int = 1000,
) -> int:
    """Append one snapshot to a user-selected SQLite file and enforce retention."""
    days = max(1, min(int(retention_days), 365))
    limit = max(1, min(int(max_entries), 10000))
    path = Path(destination).expanduser()
    now = datetime.now(UTC)
    cutoff = (now - timedelta(days=days)).isoformat(timespec="seconds")
    payload = json.dumps(snapshot.to_dict(), ensure_ascii=False, sort_keys=True)
    with sqlite3.connect(path, timeout=3) as connection:
        connection.execute("PRAGMA busy_timeout = 3000")
        connection.execute(
            "CREATE TABLE IF NOT EXISTS snapshots ("
            "id INTEGER PRIMARY KEY, saved_at TEXT NOT NULL, collected_at TEXT NOT NULL, payload TEXT NOT NULL)"
        )
        connection.execute(
            "INSERT INTO snapshots(saved_at, collected_at, payload) VALUES (?, ?, ?)",
            (now.isoformat(timespec="seconds"), snapshot.collected_at, payload),
        )
        connection.execute("DELETE FROM snapshots WHERE saved_at < ?", (cutoff,))
        connection.execute(
            "DELETE FROM snapshots WHERE id NOT IN ("
            "SELECT id FROM snapshots ORDER BY saved_at DESC, id DESC LIMIT ?)",
            (limit,),
        )
        count = connection.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0]
    return int(count)


def read_snapshot_history(destination: str | Path, *, limit: int = 100) -> list[dict[str, object]]:
    """Read a bounded number of newest records from an existing local history file."""
    maximum = max(1, min(int(limit), 1000))
    path = Path(destination).expanduser()
    if not path.is_file():
        return []
    with sqlite3.connect(path, timeout=3) as connection:
        rows = connection.execute(
            "SELECT saved_at, collected_at, payload FROM snapshots ORDER BY saved_at DESC, id DESC LIMIT ?",
            (maximum,),
        ).fetchall()
    return [
        {"saved_at": saved_at, "collected_at": collected_at, "snapshot": json.loads(payload)}
        for saved_at, collected_at, payload in rows
    ]
