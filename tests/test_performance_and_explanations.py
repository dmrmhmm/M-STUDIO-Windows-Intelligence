from mstudio.core.explanations import explain_metric
from mstudio.core.performance import collect_performance_sample


def test_metric_explanations_are_local_and_known():
    assert "physical memory" in explain_metric("memory_percent").lower()
    assert "no explanation" in explain_metric("unknown_metric").lower()


def test_performance_sample_has_bounded_numeric_values():
    sample = collect_performance_sample()
    for value in (sample.cpu_percent, sample.memory_percent, sample.disk_percent):
        assert value is None or 0 <= value <= 100
    assert sample.collected_at.endswith("+00:00")
