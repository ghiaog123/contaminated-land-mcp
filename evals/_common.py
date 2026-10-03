"""Shared helpers for the eval tasks. Kept tiny; nothing here calls an LLM."""

import json
import os
import re

import httpx

# (site_id, criteria_set): primary criteria set per demo site, docs/03-data.md "Demo sites".
DEMO_RUNS = [
    ("DEMO-01", "hil-a-residential"),
    ("DEMO-02", "hsl-a-b-vapour-intrusion"),
    ("DEMO-03", "hil-a-residential"),
]
CHUNK_ID = re.compile(r"[a-z0-9-]+:p\d+:\d{4}")
PLACEHOLDER = re.compile(r"<[A-Z]+(?:_[A-Z]+)*_\d+>")


def require_key() -> None:
    """Exit with a clear message instead of a stack trace when no OpenRouter key is set."""
    if not os.environ.get("OPENROUTER_API_KEY"):
        raise SystemExit(
            "OPENROUTER_API_KEY is not set: this eval calls a real model. Export it (never commit it) and rerun."
        )


class RecordingTransport(httpx.BaseTransport):
    """Records every request body and response body (never headers, so never the API key), then delegates."""

    def __init__(self, inner: httpx.BaseTransport):
        self.inner = inner
        self.requests: list[str] = []
        self.responses: list[str] = []

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request.read().decode("utf-8", "replace"))
        response = self.inner.handle_request(request)
        response.read()
        self.responses.append(response.text)
        return response


def request_text(body: str) -> str:
    """Chat-completions request body -> all message text, JSON-decoded (so \\u escapes cannot hide a string)."""
    try:
        msgs = json.loads(body).get("messages", [])
    except ValueError:
        return body
    return "\n".join(m["content"] if isinstance(m.get("content"), str) else json.dumps(m.get("content")) for m in msgs)


def reply_text(body: str) -> str:
    try:
        return json.loads(body)["choices"][0]["message"]["content"] or ""
    except (ValueError, KeyError, IndexError, TypeError):
        return ""
