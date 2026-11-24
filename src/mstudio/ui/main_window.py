"""Minimal, accessible diagnostics dashboard with explicit refresh."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from mstudio.core.diagnostics import collect_snapshot
from mstudio.core.models import SystemSnapshot


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
    return {
        "OPERATING SYSTEM": snapshot.operating_system,
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


class MainWindow(QMainWindow):
    def __init__(
        self,
        snapshot: SystemSnapshot,
        refresh_callback: Callable[[], SystemSnapshot] = collect_snapshot,
    ) -> None:
        super().__init__()
        self._refresh_callback = refresh_callback
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
            content.setWordWrap(True)
            self._value_labels[label] = content
            card_layout.addWidget(heading)
            card_layout.addWidget(content)
            grid.addWidget(card, index // 2, index % 2)
        layout.addWidget(grid_host)

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
            QLabel#warning { color: #f0c674; }
            QLabel#footer { font-size: 10px; padding-top: 10px; }
            QPushButton#refreshButton { background: #29465b; border: 1px solid #52738c;
                border-radius: 6px; padding: 8px 16px; font-weight: 600; }
            QPushButton#refreshButton:hover { background: #365d78; }
            QPushButton#refreshButton:disabled { color: #71808d; }
        """)
        self._apply_snapshot(snapshot)

    def _apply_snapshot(self, snapshot: SystemSnapshot) -> None:
        for label, value in _snapshot_values(snapshot).items():
            self._value_labels[label].setText(value)
        self._warning_label.setText("\n".join(snapshot.warnings))
        self._footer.setText(
            f"Collected: {snapshot.collected_at}  |  M / STUDIO 0.1.0"
        )

    def refresh_snapshot(self) -> None:
        """Refresh displayed metrics without changing system state."""
        self.refresh_button.setEnabled(False)
        self.refresh_button.setText("Refreshing…")
        try:
            self._apply_snapshot(self._refresh_callback())
        except Exception as exc:  # Keep the existing dashboard usable on refresh errors.
            self._warning_label.setText(
                f"Refresh failed: {type(exc).__name__}: {exc}"
            )
        finally:
            self.refresh_button.setText("Refresh")
            self.refresh_button.setEnabled(True)
