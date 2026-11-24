"""Bounded live performance view; sampling stops when the dialog closes."""
from __future__ import annotations

from collections import deque

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout

from mstudio.core.performance import PerformanceSample, collect_performance_sample


class LivePerformanceDialog(QDialog):
    def __init__(self, parent=None, *, interval_ms: int = 1000, max_samples: int = 60) -> None:
        super().__init__(parent)
        self.setWindowTitle("M / STUDIO | Live performance")
        self.setMinimumWidth(460)
        self._samples: deque[PerformanceSample] = deque(maxlen=max(1, min(int(max_samples), 60)))
        self._label = QLabel("Collecting local performance samples…")
        self._label.setWordWrap(True)
        layout = QVBoxLayout(self)
        layout.addWidget(self._label)
        self._timer = QTimer(self)
        self._timer.setInterval(max(500, min(int(interval_ms), 5000)))
        self._timer.timeout.connect(self.collect_sample)
        self.finished.connect(lambda _result: self._timer.stop())
        self.collect_sample()
        self._timer.start()

    @property
    def samples(self) -> tuple[PerformanceSample, ...]:
        return tuple(self._samples)

    def collect_sample(self) -> None:
        sample = collect_performance_sample()
        self._samples.append(sample)
        self._label.setText(self._format_samples())

    def _format_samples(self) -> str:
        def sparkline(key: str) -> str:
            levels = "▁▂▃▄▅▆▇█"
            values = [getattr(item, key) for item in self._samples]
            return "".join(
                levels[min(7, max(0, int(value // 12.5)))] if value is not None else "·"
                for value in values
            )

        latest = self._samples[-1]
        def display(value: float | None) -> str:
            return f"{value:.1f}%" if value is not None else "unavailable"

        return "\n".join((
            f"CPU: {display(latest.cpu_percent)}  {sparkline('cpu_percent')}",
            f"Memory: {display(latest.memory_percent)}  {sparkline('memory_percent')}",
            f"System disk: {display(latest.disk_percent)}  {sparkline('disk_percent')}",
            f"Samples retained: {len(self._samples)} / {self._samples.maxlen}",
            f"Latest sample: {latest.collected_at}",
            "Sampling is local and stops when this window closes.",
        ))

    def closeEvent(self, event) -> None:
        self._timer.stop()
        super().closeEvent(event)
