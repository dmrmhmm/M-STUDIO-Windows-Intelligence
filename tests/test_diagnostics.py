from mstudio.core.diagnostics import collect_snapshot
from mstudio.core.models import SystemSnapshot


def test_snapshot_has_platform_metadata():
    snapshot = collect_snapshot()
    assert isinstance(snapshot, SystemSnapshot)
    assert snapshot.operating_system
    assert snapshot.collected_at.endswith("+00:00")


def test_snapshot_serializes():
    snapshot = SystemSnapshot(operating_system="Test OS", hostname="test-host")
    data = snapshot.to_dict()
    assert data["operating_system"] == "Test OS"
    assert data["hostname"] == "test-host"
    assert isinstance(data["warnings"], list)


def test_metrics_are_non_negative_when_available():
    snapshot = collect_snapshot()
    for value in (
        snapshot.logical_cores,
        snapshot.memory_total_bytes,
        snapshot.memory_available_bytes,
        snapshot.disk_total_bytes,
        snapshot.disk_free_bytes,
    ):
        assert value is None or value >= 0
