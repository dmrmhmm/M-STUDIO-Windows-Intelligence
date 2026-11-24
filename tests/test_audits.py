from mstudio.adapters import powershell
from mstudio.core import audits


def test_driver_query_is_fixed_and_bounded(monkeypatch):
    calls = []

    def fake_query(command, timeout_seconds):
        calls.append((command, timeout_seconds))
        return [{"DeviceName": "Example device", "IsSigned": True}]

    monkeypatch.setattr(powershell, "_run_fixed_query", fake_query)
    result = powershell.get_windows_driver_inventory(timeout_seconds=99)
    assert result == [{"DeviceName": "Example device", "IsSigned": True}]
    assert calls[0][1] == 99
    assert "Win32_PnPSignedDriver" in calls[0][0]
    assert "Select-Object -First 100" in calls[0][0]


def test_security_query_returns_only_structured_data(monkeypatch):
    monkeypatch.setattr(
        powershell, "_run_fixed_query",
        lambda command, timeout_seconds: {"Defender": None, "Firewall": []},
    )
    assert powershell.get_windows_security_status() == {"Defender": None, "Firewall": []}


def test_audits_report_unsupported_platform(monkeypatch):
    monkeypatch.setattr(audits.platform, "system", lambda: "Linux")
    assert audits.audit_drivers()["available"] is False
    assert audits.audit_security()["available"] is False


def test_audit_does_not_claim_missing_data_is_safe(monkeypatch):
    monkeypatch.setattr(audits.platform, "system", lambda: "Windows")
    monkeypatch.setattr(audits, "get_windows_security_status", lambda timeout_seconds: None)
    result = audits.audit_security()
    assert result["available"] is False
    assert "unavailable" in result["reason"].lower()
