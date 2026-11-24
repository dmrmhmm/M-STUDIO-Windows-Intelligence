import pytest
from PySide6.QtCore import QEventLoop, QThreadPool, QTimer
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



def test_dashboard_displays_explainable_recommendations(qapp):
    window = MainWindow(SystemSnapshot(memory_percent=92))
    insights = window.findChild(QLabel, "insights")
    assert insights is not None
    assert "Review memory usage" in insights.text()
    assert "Memory pressure is elevated" in insights.text()


def test_system_audit_runs_off_ui_thread_and_reports_read_only_result(qapp, monkeypatch):
    from mstudio.ui import main_window

    monkeypatch.setattr(
        main_window, "audit_drivers",
        lambda: {"available": True, "count": 12, "drivers": []},
    )
    monkeypatch.setattr(
        main_window, "audit_security",
        lambda: {"available": True, "status": {"Defender": {}, "Firewall": [{"Name": "Domain"}]}},
    )
    messages = []
    monkeypatch.setattr(
        main_window.QMessageBox, "information",
        lambda *args: messages.append(args),
    )
    window = MainWindow(SystemSnapshot())
    loop = QEventLoop()
    outcomes = []
    window.audit_finished.connect(lambda success: (outcomes.append(success), loop.quit()))

    window.run_system_audit()
    assert not window.audit_button.isEnabled()
    assert QThreadPool.globalInstance().waitForDone(5000)
    qapp.processEvents()

    assert outcomes == [True]
    assert window.audit_button.isEnabled()
    assert "12 entries" in messages[0][2]
    assert "No settings or drivers were changed." in messages[0][2]


def test_storage_button_reports_read_only_volume_inventory(qapp, monkeypatch):
    from types import SimpleNamespace
    from mstudio.ui import main_window

    monkeypatch.setattr(
        main_window, "collect_storage_volumes",
        lambda: [SimpleNamespace(mountpoint="C:\\", filesystem="NTFS", percent_used=50.0,
                                 free_bytes=500, total_bytes=1000)],
    )
    messages = []
    monkeypatch.setattr(main_window.QMessageBox, "information", lambda *args: messages.append(args))
    window = MainWindow(SystemSnapshot())
    outcomes = []
    window.storage_finished.connect(outcomes.append)
    window.inspect_storage()
    assert not window.storage_button.isEnabled()
    assert QThreadPool.globalInstance().waitForDone(5000)
    qapp.processEvents()
    assert outcomes == [True]
    assert window.storage_button.isEnabled()
    assert "50.0% used" in messages[0][2]
    assert "no files were changed" in messages[0][2].lower()


def test_history_button_saves_only_to_user_selected_local_path(qapp, tmp_path, monkeypatch):
    import sqlite3
    from mstudio.ui import main_window

    destination = tmp_path / "chosen-history.sqlite3"
    messages = []
    monkeypatch.setattr(main_window.QMessageBox, "information", lambda *args: messages.append(args))
    window = MainWindow(SystemSnapshot(hostname="history-host"))
    window.save_history(str(destination))
    assert destination.exists()
    with sqlite3.connect(destination) as connection:
        payload = connection.execute("SELECT payload FROM snapshots").fetchone()[0]
    assert "history-host" in payload
    assert "30 days / 1,000 records" in messages[0][2]


def test_local_ai_requires_explicit_model_choice_and_runs_in_worker(qapp, monkeypatch):
    from mstudio.ui import main_window

    requested = []
    shown = []
    monkeypatch.setattr(main_window.QInputDialog, "getText",
                        lambda *args: ("local-test-model", True))
    monkeypatch.setattr(main_window, "explain_with_local_model",
                        lambda prompt, model, enabled: requested.append((prompt, model, enabled)) or "Local explanation")
    monkeypatch.setattr(main_window.QMessageBox, "information", lambda *args: shown.append(args))
    window = MainWindow(SystemSnapshot(memory_percent=88, warnings=["Memory elevated"]))
    outcomes = []
    window.local_ai_finished.connect(outcomes.append)
    window.request_local_ai_explanation()
    assert not window.local_ai_button.isEnabled()
    assert QThreadPool.globalInstance().waitForDone(5000)
    qapp.processEvents()
    assert outcomes == [True]
    assert requested and requested[0][1:] == ("local-test-model", True)
    assert "Memory elevated" in requested[0][0]
    assert shown[0][2] == "Local explanation"


def test_local_ai_cancel_does_not_start_worker(qapp, monkeypatch):
    from mstudio.ui import main_window

    monkeypatch.setattr(main_window.QInputDialog, "getText", lambda *args: ("", False))
    window = MainWindow(SystemSnapshot())
    window.request_local_ai_explanation()
    assert window._local_ai_worker is None
    assert window.local_ai_button.isEnabled()
