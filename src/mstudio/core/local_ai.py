"""Explicit opt-in explanations through a loopback-only local Ollama service."""
from __future__ import annotations

import json
import re
from urllib.error import URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

_MODEL_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,79}$")
_ENDPOINT = "http://127.0.0.1:11434/api/generate"


class _RejectRedirects(HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        return None


def _open_local(request: Request, timeout: int):
    return build_opener(_RejectRedirects()).open(request, timeout=timeout)


def explain_with_local_model(text: str, model: str, *, enabled: bool = False, timeout: int = 15) -> str | None:
    """Ask a local Ollama model to explain supplied diagnostics; never contacts remote hosts."""
    if not enabled:
        return None
    model_name = model.strip()
    if not _MODEL_PATTERN.fullmatch(model_name):
        raise ValueError("Model name contains unsupported characters.")
    diagnostic_text = str(text)[:2000]
    prompt = (
        "Explain these Windows diagnostic observations in plain language. "
        "Do not recommend running commands, changing settings, deleting files, or disabling security. "
        "State uncertainty and keep the answer under 180 words.\n\n"
        + diagnostic_text
    )
    payload = json.dumps({
        "model": model_name, "prompt": prompt, "stream": False,
        "options": {"temperature": 0.2, "num_predict": 220},
    }).encode("utf-8")
    request = Request(_ENDPOINT, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with _open_local(request, timeout=max(2, min(int(timeout), 20))) as response:
            raw = response.read(65537)
    except (OSError, URLError, TimeoutError) as exc:
        raise RuntimeError("Local Ollama service is unavailable on 127.0.0.1:11434.") from exc
    if len(raw) > 65536:
        raise RuntimeError("Local model response exceeded the 64 KiB safety limit.")
    try:
        result = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Local model returned an invalid response.") from exc
    explanation = result.get("response") if isinstance(result, dict) else None
    if not isinstance(explanation, str) or not explanation.strip():
        raise RuntimeError("Local model did not return an explanation.")
    return explanation.strip()[:4000]
