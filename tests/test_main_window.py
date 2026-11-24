import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication

from mstudio.core.models import SystemSnapshot
from mstudio.ui.main_window import MainWindow


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def test_refresh_button_updates_snapshot(qapp):
    initial = SystemSnapshot(hostname="before", collected_at="initial")
    refreshed = SystemSnapshot(hostname="after", collected_at="refreshed")
    window = MainWindow(initial, refresh_callback=lambda: refreshed)

    window.refresh_button.click()

    assert window._value_labels["DEVICE"].text() == "after"
    assert "refreshed" in window._footer.text()
    assert window.refresh_button.isEnabled()


def test_refresh_error_keeps_dashboard_available(qapp):
    initial = SystemSnapshot(hostname="still visible")

    def fail_refresh():
        raise OSError("temporary read failure")

    window = MainWindow(initial, refresh_callback=fail_refresh)
    window.refresh_button.click()

    assert window._value_labels["DEVICE"].text() == "still visible"
    assert "Refresh failed: OSError" in window._warning_label.text()
    assert window.refresh_button.isEnabled()
