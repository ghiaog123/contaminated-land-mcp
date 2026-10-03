"""One OpenRouter client (OpenAI-compatible, openai SDK 3.x). The http_client parameter is the
injection point for the pii_leak recording transport and for stub tests:
    LLM(http_client=httpx.Client(transport=httpx.MockTransport(handler)))
"""

import os

import httpx
import openai

from contaminated_land.paths import ROOT
from contaminated_land.types import LLMReply

DEFAULT_MODEL = "deepseek/deepseek-v4.1-flash"
BASE_URL = "https://openrouter.ai/api/v1"


class MissingAPIKey(RuntimeError):
    pass


def _dotenv(name: str) -> str | None:
    """Value of `name` from ROOT/.env (KEY=VALUE lines only). ponytail: no quoting rules beyond stripping quotes."""
    try:
        for line in (ROOT / ".env").read_text().splitlines():
            k, sep, v = line.partition("=")
            if sep and k.strip() == name:
                return v.strip().strip("'\"") or None
    except OSError:
        pass
    return None


class LLM:
    def __init__(self, model: str | None = None, api_key: str | None = None, http_client: httpx.Client | None = None):
        """model defaults to $CONTAMINATED_LAND_MODEL then DEFAULT_MODEL; api_key to $OPENROUTER_API_KEY (then .env).
        Raise MissingAPIKey (clear message, never the key) when no key and no http_client is given."""
        env = "CONTAMINATED_LAND_MODEL"
        self.model = model or os.environ.get(env) or _dotenv(env) or DEFAULT_MODEL
        key = api_key or os.environ.get("OPENROUTER_API_KEY") or _dotenv("OPENROUTER_API_KEY")
        if not key:
            if http_client is None:
                raise MissingAPIKey(
                    "OPENROUTER_API_KEY is not set. Put OPENROUTER_API_KEY=... in .env (see .env.example)."
                )
            key = "dummy-key-for-injected-client"
        self._client = openai.OpenAI(base_url=BASE_URL, api_key=key, http_client=http_client)

    def complete(self, messages: list[dict], temperature: float = 0.0) -> LLMReply:
        r = self._client.chat.completions.create(model=self.model, messages=messages, temperature=temperature)
        u = r.usage
        return LLMReply(
            text=r.choices[0].message.content or "",
            model=r.model or self.model,
            input_tokens=u.prompt_tokens if u else 0,
            output_tokens=u.completion_tokens if u else 0,
        )
