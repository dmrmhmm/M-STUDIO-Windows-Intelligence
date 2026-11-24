"""PySide6 application bootstrap."""

from __future__ import annotations

import sys

from mstudio.core.diagnostics import collect_snapshot


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
    window = MainWindow(collect_snapshot())
    window.show()
    return app.exec()
