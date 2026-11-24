from mstudio.core.history import read_snapshot_history, save_snapshot_history
from mstudio.core.models import SystemSnapshot


def test_history_is_explicit_local_and_round_trips_snapshot(tmp_path):
    destination = tmp_path / "history.sqlite3"
    assert not destination.exists()
    count = save_snapshot_history(
        SystemSnapshot(hostname="local-device", memory_percent=42.0), destination
    )
    assert count == 1
    records = read_snapshot_history(destination)
    assert records[0]["snapshot"]["hostname"] == "local-device"
    assert records[0]["snapshot"]["memory_percent"] == 42.0


def test_history_enforces_entry_limit(tmp_path):
    destination = tmp_path / "history.sqlite3"
    for index in range(4):
        save_snapshot_history(SystemSnapshot(hostname=f"device-{index}"), destination, max_entries=2)
    records = read_snapshot_history(destination, limit=10)
    assert len(records) == 2
    assert records[0]["snapshot"]["hostname"] == "device-3"
    assert records[1]["snapshot"]["hostname"] == "device-2"


def test_history_read_does_not_create_missing_database(tmp_path):
    destination = tmp_path / "missing.sqlite3"
    assert read_snapshot_history(destination) == []
    assert not destination.exists()