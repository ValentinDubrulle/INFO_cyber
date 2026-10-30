from datetime import datetime, timezone

import pytest

from digest import summarize
from digest.models import Item


class FakeResp:
    def __init__(self, status, payload=None, text=""):
        self.status_code, self._payload, self.text = status, payload, text
        self.headers = {}

    def json(self):
        return self._payload


@pytest.fixture(autouse=True)
def reset(monkeypatch):
    summarize._DEAD.clear()
    summarize._FAILURES.clear()
    monkeypatch.setattr(summarize.time, "sleep", lambda s: None)


PROVIDERS = [
    {"name": "Gemini", "type": "gemini", "key": "k1", "models": ["g1", "g2"]},
    {"name": "Mistral", "type": "openai", "key": "k2", "base_url": "https://x/v1", "models": ["m1"]},
]


def test_falls_back_to_next_provider_when_gemini_project_is_blocked(monkeypatch):
    calls = []

    def post(url, **kw):
        calls.append(url)
        if "x/v1" in url:
            return FakeResp(200, {"choices": [{"message": {"content": "[1]"}}]})
        return FakeResp(403, text='{"error": {"message": "The Gemini API free tier is not available for this project."}}')

    monkeypatch.setattr(summarize.requests, "post", post)
    assert summarize.call_llm("p", PROVIDERS) == "[1]"
    assert len(calls) == 2  # g2 n'est pas essayé : le blocage concerne tout le compte
    assert "facturation" in summarize.failure_report()


def test_all_failed_raises_and_reports(monkeypatch):
    monkeypatch.setattr(summarize.requests, "post", lambda url, **kw: FakeResp(401, text="API key not valid"))
    with pytest.raises(summarize.LLMError):
        summarize.call_llm("p", PROVIDERS)
    assert summarize.exhausted(PROVIDERS)
    assert "clé API refusée" in summarize.failure_report()


def test_providers_without_secret_are_skipped(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)
    settings = {"providers": [
        {"name": "Gemini", "type": "gemini", "key_env": "GEMINI_API_KEY", "models": ["g"]},
        {"name": "Mistral", "type": "openai", "key_env": "MISTRAL_API_KEY", "models": ["m"]},
    ]}
    assert [p["name"] for p in summarize.active_providers(settings)] == ["Gemini"]


def test_parse_extracts_array_from_prose():
    assert summarize._parse('Voici le résultat :\n[{"id": 0}]\nBonne lecture') == [{"id": 0}]


def test_fallback_digest_lists_every_item():
    now = datetime.now(timezone.utc)
    items = [Item("a", "Faille X", "https://a", "CISA KEV", now, "texte", kind="kev"),
             Item("b", "Article Y", "https://b", "Krebs", now, "mot " * 200)]
    d = summarize.fallback_digest(items, "cause")
    assert d["count"] == 2 and d["degraded"] == "cause"
    assert d["sections"]["vulnerabilites"][0]["kev"]
    assert d["sections"]["autres"][0]["resume"].endswith("…")


def test_gemini_sends_low_thinking_and_retries_without_if_refused(monkeypatch):
    bodies = []

    def post(url, json=None, **kw):
        bodies.append(dict(json["generationConfig"]))
        if "thinkingConfig" in json["generationConfig"]:
            return FakeResp(400, text="Unknown field thinkingConfig")
        return FakeResp(200, {"candidates": [{"content": {"parts": [{"text": "[]"}]}}]})

    monkeypatch.setattr(summarize.requests, "post", post)
    provider = {"name": "Gemini", "type": "gemini", "key": "k", "models": ["g"], "thinking_level": "low"}
    assert summarize.call_llm("p", [provider]) == "[]"
    assert bodies[0]["thinkingConfig"] == {"thinkingLevel": "low"}
    assert "thinkingConfig" not in bodies[1]
