"""Minimal, accessible diagnostics dashboard with background refresh."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal, Slot
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QFileDialog,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from mstudio.core.diagnostics import collect_snapshot
from mstudio.core.insights import assess_health, build_recommendations
from mstudio.core.models import SystemSnapshot
from mstudio.core.performance import collect_performance_sample
from mstudio.core.reports import export_json_report


def _format_bytes(value: int | None) -> str:
    if value is None:
        return "Unavailable"
    amount = float(value)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if amount < 1024 or unit == "TB":
            return f"{amount:.1f} {unit}"
        amount /= 1024
    return "Unavailable"


def _snapshot_values(snapshot: SystemSnapshot) -> dict[str, str]:
    health = assess_health(snapshot)
    os_name = snapshot.os_caption or snapshot.operating_system
    os_details = " · ".join(
        value
        for value in (
            f"Version {snapshot.os_version}" if snapshot.os_version else "",
            f"Build {snapshot.os_build}" if snapshot.os_build else "",
            snapshot.os_architecture,
        )
        if value
    )
    operating_system = f"{os_name}\\n{os_details}" if os_details else os_name
    return {
        "SYSTEM HEALTH": f"{health.score}/100 · {health.status}",
        "OPERATING SYSTEM": operating_system,
        "DEVICE": snapshot.hostname,
        "PROCESSOR": snapshot.processor or "Unavailable",
        "LOGICAL CORES": str(snapshot.logical_cores or "Unavailable"),
        "MEMORY": (
            f"{_format_bytes(snapshot.memory_available_bytes)} available / "
            f"{_format_bytes(snapshot.memory_total_bytes)} total"
        ),
        "MEMORY LOAD": (
            f"{snapshot.memory_percent:.1f}%"
            if snapshot.memory_percent is not None
            else "Unavailable"
        ),
        "SYSTEM DISK": (
            f"{_format_bytes(snapshot.disk_free_bytes)} free / "
            f"{_format_bytes(snapshot.disk_total_bytes)} total"
        ),
        "DISK USAGE": (
            f"{snapshot.disk_percent:.1f}%"
            if snapshot.disk_percent is not None
            else "Unavailable"
        ),
    }


class _RefreshSignals(QObject):
    finished = Signal(object, object)


class _RefreshWorker(QRunnable):
    def __init__(self, callback: Callable[[], SystemSnapshot]) -> None:
        super().__init__()
        self.callback = callback
        self.signals = _RefreshSignals()

    @Slot()
    def run(self) -> None:
        try:
            snapshot = self.callback()
            if not isinstance(snapshot, SystemSnapshot):
                raise TypeError("Refresh provider must return a SystemSnapshot.")
        except Exception as exc:  # Convert provider failures into UI-safe results.  # noqa: BLE001
            self.signals.finished.emit(None, f"{type(exc).__name__}: {exc}")
        else:
            self.signals.finished.emit(snapshot, None)


class MainWindow(QMainWindow):
    refresh_finished = Signal(bool)

    def __init__(
        self,
        snapshot: SystemSnapshot,
        refresh_callback: Callable[[], SystemSnapshot] = collect_snapshot,
    ) -> None:
        super().__init__()
        self._refresh_callback = refresh_callback
        self._current_snapshot = snapshot
        self._refresh_worker: _RefreshWorker | None = None
        self.setWindowTitle("M / STUDIO | Windows Intelligence")
        self.resize(900, 620)
        self.setMinimumSize(640, 460)
        self._value_labels: dict[str, QLabel] = {}

        root = QWidget()
        layout = QVBoxLayout(root)

        header = QHBoxLayout()
        headings = QVBoxLayout()
        title = QLabel("M / STUDIO")
        title.setObjectName("title")
        subtitle = QLabel("SYSTEM INTELLIGENCE  /  READ-ONLY DIAGNOSTICS")
        subtitle.setObjectName("subtitle")
        headings.addWidget(title)
        headings.addWidget(subtitle)
        header.addLayout(headings)
        header.addStretch(1)
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setObjectName("refreshButton")
        self.refresh_button.setToolTip("Collect a new read-only system snapshot")
        self.refresh_button.clicked.connect(self.refresh_snapshot)
        header.addWidget(self.refresh_button)
        self.performance_button = QPushButton("Performance")
        self.performance_button.setObjectName("performanceButton")
        self.performance_button.setToolTip("Take one on-demand local performance sample")
        self.performance_button.clicked.connect(self.show_performance_sample)
        header.addWidget(self.performance_button)
        self.export_button = QPushButton("Export report")
        self.export_button.setObjectName("exportButton")
        self.export_button.setToolTip("Save a local JSON diagnostics report")
        self.export_button.clicked.connect(self.choose_report_destination)
        header.addWidget(self.export_button)
        layout.addLayout(header)

        grid_host = QWidget()
        grid = QGridLayout(grid_host)
        for index, (label, value) in enumerate(_snapshot_values(snapshot).items()):
            card = QWidget()
            card.setObjectName("metricCard")
            card_layout = QVBoxLayout(card)
            heading = QLabel(label)
            heading.setObjectName("metricLabel")
            content = QLabel(value)
            content.setObjectName("metricValue")
            content.setProperty("metricKey", label)
            content.setWordWrap(True)
            self._value_labels[label] = content
            card_layout.addWidget(heading)
            card_layout.addWidget(content)
            grid.addWidget(card, index // 2, index % 2)
        layout.addWidget(grid_host)

        self._insight_label = QLabel()
        self._insight_label.setObjectName("insights")
        self._insight_label.setWordWrap(True)
        layout.addWidget(self._insight_label)

        status = QLabel(
            "SAFE MODE ACTIVE  •  No settings, services, registry keys, or files were changed."
        )
        status.setObjectName("status")
        status.setWordWrap(True)
        layout.addWidget(status)
        self._warning_label = QLabel()
        self._warning_label.setObjectName("warning")
        self._warning_label.setWordWrap(True)
        layout.addWidget(self._warning_label)

        self._footer = QLabel()
        self._footer.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._footer.setObjectName("footer")
        layout.addWidget(self._footer)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(root)
        self.setCentralWidget(scroll)
        self.setStyleSheet("""
            QMainWindow, QScrollArea, QWidget { background: #111820; color: #e7edf3; }
            QLabel#title { font-size: 28px; font-weight: 700; letter-spacing: 2px; }
            QLabel#subtitle, QLabel#metricLabel, QLabel#footer { color: #91a3b5; }
            QLabel#subtitle { font-size: 10px; letter-spacing: 2px; margin-bottom: 12px; }
            QWidget#metricCard { background: #1b2733; border: 1px solid #304252; border-radius: 8px; }
            QLabel#metricLabel { font-size: 10px; font-weight: 700; }
            QLabel#metricValue { font-size: 16px; font-weight: 600; padding-top: 5px; }
            QLabel#status { color: #8fd3b2; padding: 12px 4px; }
            QLabel#warning { color: #f0c674; }\n            QLabel#insights { color: #b9d7ed; padding: 8px 4px; }
            QLabel#footer { font-size: 10px; padding-top: 10px; }
            QPushButton#refreshButton { background: #29465b; border: 1px solid #52738c;
                border-radius: 6px; padding: 8px 16px; font-weight: 600; }
            QPushButton#refreshButton:hover { background: #365d78; }
            QPushButton#refreshButton:disabled { color: #71808d; }
        """)
        self._apply_snapshot(snapshot)

    def _apply_snapshot(self, snapshot: SystemSnapshot) -> None:
        self._current_snapshot = snapshot
        for label, value in _snapshot_values(snapshot).items():
            self._value_labels[label].setText(value)
        self._warning_label.setText("\\n".join(snapshot.warnings))
        recommendations = build_recommendations(snapshot)
        self._insight_label.setText(
            "RECOMMENDATIONS\\n" + "\\n".join(
                f"• [{item.priority}] {item.title}: {item.explanation}"
                for item in recommendations
            )
        )
        self._footer.setText(
            f"Collected: {snapshot.collected_at}  |  M / STUDIO 0.1.0"
        )

    @Slot()
    def refresh_snapshot(self) -> None:
        """Collect a snapshot on the shared Qt thread pool without blocking the UI."""
        if self._refresh_worker is not None:
            return
        self.refresh_button.setEnabled(False)
        self.refresh_button.setText("Refreshing…")
        worker = _RefreshWorker(self._refresh_callback)
        worker.signals.finished.connect(self._finish_refresh)
        self._refresh_worker = worker
        QThreadPool.globalInstance().start(worker)

    @Slot(object, object)
    def _finish_refresh(self, snapshot: object, error: object) -> None:
        succeeded = isinstance(snapshot, SystemSnapshot) and error is None
        if succeeded:
            self._apply_snapshot(snapshot)
        else:
            self._warning_label.setText(f"Refresh failed: {error or 'Unknown provider error'}")
        self._refresh_worker = None
        self.refresh_button.setText("Refresh")
        self.refresh_button.setEnabled(True)
        self.refresh_finished.emit(succeeded)

    @Slot()
    def show_performance_sample(self) -> None:
        """Show one local sample; no polling or network activity is started."""
        sample = collect_performance_sample()
        values = (
            f"CPU: {sample.cpu_percent:.1f}%" if sample.cpu_percent is not None else "CPU: unavailable",
            f"Memory: {sample.memory_percent:.1f}%" if sample.memory_percent is not None else "Memory: unavailable",
            f"System disk: {sample.disk_percent:.1f}%" if sample.disk_percent is not None else "System disk: unavailable",
        )
        QMessageBox.information(
            self,
            "Performance snapshot",
            "\\n".join((*values, f"Collected: {sample.collected_at}")),
        )

    @Slot()
    def choose_report_destination(self) -> None:
        destination, _ = QFileDialog.getSaveFileName(
            self, "Export diagnostics report", "mstudio-diagnostics.json",
            "JSON report (*.json)",
        )
        if destination:
            self.export_report(destination)

    def export_report(self, destination: str) -> None:
        """Export the currently displayed snapshot to a user-selected local path."""
        try:
            export_json_report(self._current_snapshot, destination)
        except OSError as exc:
            QMessageBox.warning(self, "Report export failed", f"Could not save report: {exc}")
        else:
            QMessageBox.information(self, "Report exported", f"Saved local report to:\\n{destination}")
