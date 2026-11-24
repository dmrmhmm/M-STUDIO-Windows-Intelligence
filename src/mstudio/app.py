"""PySide6 application bootstrap."""

from __future__ import annotations

import platform
import sys

from mstudio.core.models import SystemSnapshot


def main() -> int:
    try:
        from PySide6.QtWidgets import QApplication
    except ImportError:
        print("PySide6 is required. Install with: python -m pip install -e .")
        return 2

    from mstudio.ui.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("M / STUDIO Windows Intelligence")
    app.setOrganizationName("M-STUDIO")

    initial_snapshot = SystemSnapshot(
        operating_system=f"{platform.system()} {platform.release()}".strip(),
        hostname=platform.node() or "Unknown",
        processor=platform.processor() or "Detecting…",
        warnings=["Initial read-only inventory is running in the background."],
    )
    window = MainWindow(initial_snapshot)
    window.show()
    window.refresh_snapshot()
    return app.exec()
