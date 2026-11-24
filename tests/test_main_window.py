import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
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


def test_refresh_button_updates_snapshot(qapp):
    initial = SystemSnapshot(hostname="before", collected_at="initial")
    refreshed = SystemSnapshot(hostname="after", collected_at="refreshed")
    window = MainWindow(initial, refresh_callback=lambda: refreshed)

    window.refresh_button.click()

    assert _metric_label(window, "DEVICE").text() == "after"
    assert "refreshed" in window.findChild(QLabel, "footer").text()
    assert window.refresh_button.isEnabled()


def test_refresh_error_keeps_dashboard_available(qapp):
    initial = SystemSnapshot(hostname="still visible")

    def fail_refresh():
        raise OSError("temporary read failure")

    window = MainWindow(initial, refresh_callback=fail_refresh)
    window.refresh_button.click()

    assert _metric_label(window, "DEVICE").text() == "still visible"
    assert "Refresh failed: OSError" in window.findChild(QLabel, "warning").text()
    assert window.refresh_button.isEnabled()
