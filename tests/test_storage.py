from mstudio.core.storage import collect_storage_volumes


def test_storage_inventory_is_bounded_and_skips_unavailable_volumes(monkeypatch):
    import psutil
    from types import SimpleNamespace

    partitions = [
        SimpleNamespace(mountpoint="/one", fstype="ext4"),
        SimpleNamespace(mountpoint="/one", fstype="ext4"),
        SimpleNamespace(mountpoint="/locked", fstype=""),
        SimpleNamespace(mountpoint="/two", fstype="ntfs"),
    ]
    monkeypatch.setattr(psutil, "disk_partitions", lambda all=False: partitions)

    class Usage:
        total = 1000
        used = 400
        free = 600
        percent = 40.0

    def usage(path):
        if path == "/locked":
            raise PermissionError("not accessible")
        return Usage()

    monkeypatch.setattr(psutil, "disk_usage", usage)
    volumes = collect_storage_volumes(max_volumes=1)
    assert len(volumes) == 1
    assert volumes[0].mountpoint == "/one"
    assert volumes[0].percent_used == 40.0


def test_storage_limit_is_clamped(monkeypatch):
    import psutil
    from types import SimpleNamespace

    monkeypatch.setattr(
        psutil, "disk_partitions",
        lambda all=False: [SimpleNamespace(mountpoint=f"/{i}", fstype="test") for i in range(40)],
    )
    monkeypatch.setattr(
        psutil, "disk_usage",
        lambda path: type("Usage", (), {"total": 10, "used": 5, "free": 5, "percent": 50.0})(),
    )
    assert len(collect_storage_volumes(max_volumes=500)) == 32
