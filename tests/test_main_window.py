import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QEventLoop, QTimer
from PySide6.QtWidgets import QApplication, QLabel

from mstudio.core.models import SystemSnapshot
from mstudio.ui.main_window import MainWindow


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def _metric_label(window: MainWindow, metric_key: str) -> QLabel:
    for label in window.findChildren(QLabel, "metricValue"):
        if label.property("metricKey") == metric_key:
            return label
    raise AssertionError(f"Metric label not found: {metric_key}")


def _wait_for_refresh(window: MainWindow) -> bool:
    loop = QEventLoop()
    outcome: list[bool] = []
    window.refresh_finished.connect(lambda succeeded: (outcome.append(succeeded), loop.quit()))
    QTimer.singleShot(5000, loop.quit)
    loop.exec()
    assert outcome, "Refresh did not finish within five seconds."
    return outcome[0]


def test_refresh_button_updates_snapshot(qapp):
    initial = SystemSnapshot(hostname="before", collected_at="initial")
    refreshed = SystemSnapshot(hostname="after", collected_at="refreshed")
    window = MainWindow(initial, refresh_callback=lambda: refreshed)

    window.refresh_button.click()
    assert not window.refresh_button.isEnabled()
    assert _wait_for_refresh(window)

    assert _metric_label(window, "DEVICE").text() == "after"
    assert "refreshed" in window.findChild(QLabel, "footer").text()
    assert window.refresh_button.isEnabled()


def test_refresh_error_keeps_dashboard_available(qapp):
    initial = SystemSnapshot(hostname="still visible")

    def fail_refresh():
        raise OSError("temporary read failure")

    window = MainWindow(initial, refresh_callback=fail_refresh)
    window.refresh_button.click()
    assert not window.refresh_button.isEnabled()
    assert not _wait_for_refresh(window)

    assert _metric_label(window, "DEVICE").text() == "still visible"
    assert "Refresh failed: OSError" in window.findChild(QLabel, "warning").text()
    assert window.refresh_button.isEnabled()


def test_refresh_rejects_non_snapshot_result(qapp):
    window = MainWindow(SystemSnapshot(hostname="unchanged"), refresh_callback=lambda: None)
    window.refresh_button.click()

    assert not _wait_for_refresh(window)
    assert _metric_label(window, "DEVICE").text() == "unchanged"
    assert "TypeError" in window.findChild(QLabel, "warning").text()



def test_export_report_uses_latest_snapshot(qapp, tmp_path, monkeypatch):
    import json
    from mstudio.ui import main_window

    window = MainWindow(SystemSnapshot(hostname="report-host"))
    messages = []
    monkeypatch.setattr(main_window.QMessageBox, "information",
                        lambda *args: messages.append(args))
    destination = tmp_path / "dashboard-report.json"
    window.export_report(str(destination))

    report = json.loads(destination.read_text(encoding="utf-8"))
    assert report["snapshot"]["hostname"] == "report-host"
    assert messages


def test_performance_button_uses_single_local_sample(qapp, monkeypatch):
    from mstudio.core.performance import PerformanceSample
    from mstudio.ui import main_window

    window = MainWindow(SystemSnapshot())
    shown = []
    monkeypatch.setattr(
        main_window, "collect_performance_sample",
        lambda: PerformanceSample("2026-11-24T00:00:00+00:00", 10.0, 20.0, 30.0),
    )
    monkeypatch.setattr(main_window.QMessageBox, "information",
                        lambda *args: shown.append(args))
    window.show_performance_sample()
    assert shown
    assert "CPU: 10.0%" in shown[0][2]
