"""Minimal, accessible diagnostics dashboard."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QMainWindow,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

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


class MainWindow(QMainWindow):
    def __init__(self, snapshot: SystemSnapshot) -> None:
        super().__init__()
        self.setWindowTitle("M / STUDIO | Windows Intelligence")
        self.resize(900, 620)
        self.setMinimumSize(640, 460)

        root = QWidget()
        layout = QVBoxLayout(root)
        title = QLabel("M / STUDIO")
        title.setObjectName("title")
        subtitle = QLabel("SYSTEM INTELLIGENCE  /  READ-ONLY DIAGNOSTICS")
        subtitle.setObjectName("subtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        grid_host = QWidget()
        grid = QGridLayout(grid_host)
        cards = [
            ("OPERATING SYSTEM", snapshot.operating_system),
            ("DEVICE", snapshot.hostname),
            ("PROCESSOR", snapshot.processor or "Unavailable"),
            ("LOGICAL CORES", str(snapshot.logical_cores or "Unavailable")),
            ("MEMORY", f"{_format_bytes(snapshot.memory_available_bytes)} available / {_format_bytes(snapshot.memory_total_bytes)} total"),
            ("MEMORY LOAD", f"{snapshot.memory_percent:.1f}%" if snapshot.memory_percent is not None else "Unavailable"),
            ("SYSTEM DISK", f"{_format_bytes(snapshot.disk_free_bytes)} free / {_format_bytes(snapshot.disk_total_bytes)} total"),
            ("DISK USAGE", f"{snapshot.disk_percent:.1f}%" if snapshot.disk_percent is not None else "Unavailable"),
        ]
        for index, (label, value) in enumerate(cards):
            card = QWidget()
            card.setObjectName("metricCard")
            card_layout = QVBoxLayout(card)
            heading = QLabel(label)
            heading.setObjectName("metricLabel")
            content = QLabel(value)
            content.setObjectName("metricValue")
            content.setWordWrap(True)
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

        if snapshot.warnings:
            warning = QLabel("\n".join(snapshot.warnings))
            warning.setObjectName("warning")
            warning.setWordWrap(True)
            layout.addWidget(warning)

        footer = QLabel(f"Collected: {snapshot.collected_at}  |  M / STUDIO 0.1.0")
        footer.setAlignment(Qt.AlignmentFlag.AlignRight)
        footer.setObjectName("footer")
        layout.addWidget(footer)

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
        """)
