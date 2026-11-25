from mstudio.core.capabilities import FEATURES
from mstudio.core.insights import assess_health, build_recommendations, diagnose_warnings
from mstudio.core.maintenance import build_maintenance_preview
from mstudio.core.models import SystemSnapshot
from mstudio.core.reports import build_report, export_json_report


def test_health_score_flags_high_memory_and_low_disk():
    snapshot = SystemSnapshot(memory_percent=92, disk_percent=96)
    health = assess_health(snapshot)
    assert health.score == 45
    assert health.status == "Critical"
    assert len(health.findings) == 2


def test_recommendations_are_advisory_only():
    snapshot = SystemSnapshot(memory_percent=85, warnings=["Disk metrics unavailable"])
    recommendations = build_recommendations(snapshot)
    assert recommendations
    assert all("does not change" in item.action for item in recommendations)


def test_warning_diagnosis_does_not_claim_root_cause():
    snapshot = SystemSnapshot(warnings=["Disk metrics could not be read"])
    result = diagnose_warnings(snapshot)
    assert result[0]["category"] == "storage"
    assert "not established" in result[0]["certainty"]


def test_report_export_is_local_and_serializable(tmp_path):
    snapshot = SystemSnapshot(hostname="test-machine", memory_percent=12.0)
    report = build_report(snapshot)
    assert report["snapshot"]["hostname"] == "test-machine"
    path = export_json_report(snapshot, tmp_path / "diagnostics.json")
    assert path.exists()
    assert '"report_version": 1' in path.read_text(encoding="utf-8")


def test_maintenance_preview_never_executes():
    preview = build_maintenance_preview("Review", "Reason", "Proposed change")
    assert preview.requires_confirmation is True
    assert preview.executable is False


def test_ten_capabilities_are_registered():
    assert len(FEATURES) == 10
    assert len({item[0] for item in FEATURES}) == 10
def test_health_assessment_is_unknown_without_usable_measurements():
    snapshot = SystemSnapshot()
    health = assess_health(snapshot)

    assert health.score is None
    assert health.status == "Insufficient data"
    assert "cannot be assessed" in health.findings[0]

    recommendations = build_recommendations(snapshot)
    assert recommendations[0].title == "Health assessment unavailable"
