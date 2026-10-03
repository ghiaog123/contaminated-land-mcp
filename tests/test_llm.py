import json

import httpx
import pytest

from contaminated_land import llm as llm_mod
from contaminated_land.llm import DEFAULT_MODEL, LLM, MissingAPIKey


def chat_response(text: str, model: str = "mock/model") -> dict:
    return {
        "id": "x",
        "object": "chat.completion",
        "created": 0,
        "model": model,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 7, "completion_tokens": 3, "total_tokens": 10},
    }


def mock_client(replies: list[str], seen: list | None = None) -> httpx.Client:
    it = iter(replies)

    def handler(request: httpx.Request) -> httpx.Response:
        if seen is not None:
            seen.append(request)
        return httpx.Response(200, json=chat_response(next(it)))

    return httpx.Client(transport=httpx.MockTransport(handler))


@pytest.fixture(autouse=True)
def clean_env(monkeypatch, tmp_path):
    for k in ("OPENROUTER_API_KEY", "CONTAMINATED_LAND_MODEL"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setattr(llm_mod, "ROOT", tmp_path)  # no real .env


def test_missing_key_raises_without_leaking():
    with pytest.raises(MissingAPIKey, match="OPENROUTER_API_KEY"):
        LLM()


def test_model_resolution(monkeypatch):
    assert LLM(http_client=mock_client([])).model == DEFAULT_MODEL
    monkeypatch.setenv("CONTAMINATED_LAND_MODEL", "env/model")
    assert LLM(http_client=mock_client([])).model == "env/model"
    assert LLM(model="arg/model", http_client=mock_client([])).model == "arg/model"


def test_key_from_env_and_dotenv(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    LLM()
    monkeypatch.delenv("OPENROUTER_API_KEY")
    (tmp_path / ".env").write_text("OPENROUTER_API_KEY='k2'\n")
    LLM()


def test_complete_goes_to_mock_and_returns_reply():
    seen = []
    reply = LLM(http_client=mock_client(["hello"], seen)).complete([{"role": "user", "content": "hi"}])
    assert reply == {"text": "hello", "model": "mock/model", "input_tokens": 7, "output_tokens": 3}
    body = json.loads(seen[0].content)
    assert seen[0].url.host == "openrouter.ai"
    assert body["model"] == DEFAULT_MODEL and body["messages"][0]["content"] == "hi"
