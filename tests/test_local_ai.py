import json

import pytest

from mstudio.core import local_ai


def test_local_ai_disabled_never_contacts_service(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("network call must not happen when disabled")
    monkeypatch.setattr(local_ai, "urlopen", forbidden)
    assert local_ai.explain_with_local_model("diagnostics", "qwen2.5:1.5b") is None


def test_local_ai_uses_only_loopback_endpoint_and_bounds_request(monkeypatch):
    seen = {}
    class Response:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def read(self, size):
            seen["read_limit"] = size
            return json.dumps({"response": "Memory use is elevated."}).encode()
    def fake_urlopen(request, timeout):
        seen["url"] = request.full_url
        seen["body"] = json.loads(request.data)
        seen["timeout"] = timeout
        return Response()
    monkeypatch.setattr(local_ai, "urlopen", fake_urlopen)
    result = local_ai.explain_with_local_model("x" * 5000, "qwen2.5:1.5b", enabled=True)
    assert result == "Memory use is elevated."
    assert seen["url"] == "http://127.0.0.1:11434/api/generate"
    assert len(seen["body"]["prompt"]) < 2300
    assert seen["timeout"] == 15
    assert seen["read_limit"] == 65537


def test_local_ai_rejects_invalid_model_names_before_network(monkeypatch):
    monkeypatch.setattr(local_ai, "urlopen", lambda *args, **kwargs: pytest.fail("unexpected request"))
    with pytest.raises(ValueError):
        local_ai.explain_with_local_model("diagnostics", "http://example.com", enabled=True)
