from mstudio.core.performance import PerformanceSample
from mstudio.ui import performance_dialog
from mstudio.ui.performance_dialog import LivePerformanceDialog


def test_live_monitor_keeps_bounded_samples_and_stops_on_close(qapp, monkeypatch):
    samples = iter([
        PerformanceSample("t1", 10.0, 20.0, 30.0),
        PerformanceSample("t2", 20.0, 30.0, 40.0),
        PerformanceSample("t3", 30.0, 40.0, 50.0),
    ])
    monkeypatch.setattr(performance_dialog, "collect_performance_sample", lambda: next(samples))
    dialog = LivePerformanceDialog(interval_ms=5000, max_samples=2)
    dialog.collect_sample()
    dialog.collect_sample()
    assert len(dialog.samples) == 2
    assert dialog.samples[-1].cpu_percent == 30.0
    assert "Samples retained: 2 / 2" in dialog._label.text()
    assert dialog._timer.isActive()
    dialog.close()
    assert not dialog._timer.isActive()