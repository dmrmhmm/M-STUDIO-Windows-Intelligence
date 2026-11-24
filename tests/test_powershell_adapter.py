from types import SimpleNamespace

from mstudio.adapters import powershell


def test_processor_query_uses_fixed_command_without_shell(monkeypatch):
    calls = []

    monkeypatch.setattr(powershell.shutil, "which", lambda _name: "pwsh")

    def fake_run(args, **kwargs):
        calls.append((args, kwargs))
        return SimpleNamespace(returncode=0, stdout='"Intel(R) Core(TM) i3-1215U"')

    monkeypatch.setattr(powershell.subprocess, "run", fake_run)

    assert powershell.get_windows_processor_name(timeout_seconds=30) == (
        "Intel(R) Core(TM) i3-1215U"
    )
    args, kwargs = calls[0]
    assert args[0] == "pwsh"
    assert args[-1] == powershell._PROCESSOR_COMMAND
    assert kwargs["shell"] is False
    assert kwargs["timeout"] == 15


def test_processor_query_returns_none_on_timeout(monkeypatch):
    monkeypatch.setattr(powershell.shutil, "which", lambda _name: "pwsh")

    def timeout(*_args, **_kwargs):
        raise powershell.subprocess.TimeoutExpired("pwsh", 3)

    monkeypatch.setattr(powershell.subprocess, "run", timeout)

    assert powershell.get_windows_processor_name(timeout_seconds=3) is None
