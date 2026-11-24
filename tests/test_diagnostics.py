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


def test_disk_failure_does_not_discard_memory_metrics(monkeypatch):
    import psutil

    class Memory:
        total = 8_000_000_000
        available = 3_000_000_000
        percent = 62.5

    monkeypatch.setattr(psutil, "virtual_memory", lambda: Memory())
    monkeypatch.setattr(psutil, "disk_usage", lambda _path: (_ for _ in ()).throw(OSError("denied")))
    snapshot = collect_snapshot()
    assert snapshot.memory_total_bytes == 8_000_000_000
    assert snapshot.memory_percent == 62.5
    assert snapshot.disk_total_bytes is None
    assert any("disk" in warning.lower() for warning in snapshot.warnings)


def test_windows_snapshot_includes_bounded_os_metadata(monkeypatch):
    from mstudio.core import diagnostics

    monkeypatch.setattr(diagnostics.platform, "system", lambda: "Windows")
    monkeypatch.setattr(
        diagnostics,
        "get_windows_os_details",
        lambda timeout_seconds: {
            "Caption": "Microsoft Windows 11 Pro",
            "Version": "10.0.26100",
            "BuildNumber": "26100",
            "OSArchitecture": "64-bit",
        },
    )

    snapshot = diagnostics.collect_snapshot()

    assert snapshot.os_caption == "Microsoft Windows 11 Pro"
    assert snapshot.os_version == "10.0.26100"
    assert snapshot.os_build == "26100"
    assert snapshot.os_architecture == "64-bit"


def test_windows_processor_fallback_when_platform_name_is_missing(monkeypatch):
    from mstudio.core import diagnostics

    monkeypatch.setattr(diagnostics.platform, "system", lambda: "Windows")
    monkeypatch.setattr(diagnostics.platform, "processor", lambda: "")
    monkeypatch.setattr(diagnostics, "get_windows_os_details", lambda timeout_seconds: None)
    monkeypatch.setattr(
        diagnostics,
        "get_windows_processor_name",
        lambda timeout_seconds: "Intel(R) Core(TM) i3-1215U",
    )

    snapshot = diagnostics.collect_snapshot()

    assert snapshot.processor == "Intel(R) Core(TM) i3-1215U"
