"""Task 4 (docs/04-evaluation.md): no client identifier reaches the model provider. GATE: 0 leaks.

  uv run --frozen --no-sync inspect eval evals/pii_leak.py                    # echo model; needs the search index
  uv run --frozen --no-sync inspect eval evals/pii_leak.py -T offline=true    # echo model + fixed passages, no key
  uv run --frozen --no-sync inspect eval evals/pii_leak.py -T real=true       # real OpenRouter call, needs the key

A recording httpx transport stores every outbound request body. Offline, the fake model echoes every
<PLACEHOLDER_n> it receives (each cited to a supplied chunk id so the validator keeps it), which also proves the
round trip. Scope: the provider boundary only; the restored draft going to the host model is not a leak here.
draft_section retrieves passages, so without the index the task stops with a clear message unless offline=true,
which swaps retrieval.search for FIXED_PASSAGES (the redaction path under test does not depend on passage content).
"""

import re

import httpx
import yaml
from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import CORRECT, INCORRECT, Score, Target, accuracy, scorer
from inspect_ai.solver import Generate, TaskState, solver

try:
    from _common import CHUNK_ID, DEMO_RUNS, PLACEHOLDER, RecordingTransport, request_text, require_key
except ImportError:  # inspect loads task files by path; fall back to the package-style import
    from evals._common import CHUNK_ID, DEMO_RUNS, PLACEHOLDER, RecordingTransport, request_text, require_key

MIN_TOKEN = 4  # name/address word tokens shorter than this are not checked
# Ordinary words that are part of a fictional client name but legitimately occur in the prompt
# ("sample S1", "fuel storage" in a site story). Whole-string checks still catch the full name; this only exempts
# the lone word. Extend with care.
GENERIC_WORDS = {"sample", "fuel"}
PASSAGE_BLOCK = re.compile(r"<passage .*?</passage>", re.S)


def _echo_handler(request: httpx.Request) -> httpx.Response:
    """Fake OpenRouter: answers with a draft that mentions every placeholder it was sent."""
    text = request_text(request.read().decode())
    tokens = list(dict.fromkeys(PLACEHOLDER.findall(text)))
    cite = (CHUNK_ID.findall(text) or [""])[0]
    draft = "\n".join(f"- The record refers to {t} [{cite}]." for t in tokens)
    return httpx.Response(
        200,
        json={
            "id": "echo",
            "object": "chat.completion",
            "created": 0,
            "model": "echo/placeholders",
            "choices": [{"index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content": draft}}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        },
    )


FIXED_PASSAGES = [
    {
        "chunk_id": f"offline-doc:p{n}:000{n}",
        "doc_id": "offline-doc",
        "doc_title": "Offline fixture guidance",
        "page": n,
        "section": "",
        "text": "Soil screening levels are compared with measured results by sampling depth band.",
        "score": 1.0,
    }
    for n in (1, 2)
]


@solver
def draft_through_recorder(real: bool, offline: bool = False):
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        from contaminated_land import drafting, retrieval
        from contaminated_land.llm import LLM

        if offline:
            retrieval.search = lambda *a, **k: list(
                FIXED_PASSAGES
            )  # ponytail: process-wide patch, fine for a one-shot eval

        rec = RecordingTransport(httpx.HTTPTransport() if real else httpx.MockTransport(_echo_handler))
        res = drafting.draft_section(
            state.metadata["site_id"],
            state.metadata["criteria_set"],
            llm=LLM(http_client=httpx.Client(transport=rec, timeout=180)),
        )
        state.output.completion = res["markdown"]
        state.metadata.update(
            redactions=res["redactions"],
            model=res["model"],
            warnings=res["warnings"],
            request_count=len(rec.requests),
            sent_placeholders=sorted({t for r in rec.requests for t in PLACEHOLDER.findall(request_text(r))}),
            recorded_requests=rec.requests,  # synthetic data only; this is exactly what the provider saw
        )
        return state

    return solve


def _terms(site: dict) -> tuple[list[str], list[str]]:
    """(whole strings checked anywhere, name/address word tokens checked outside quoted guidance passages)."""
    name, addr = site["client_name"], site["site_address"]
    whole = [name, addr] + [p.strip() for p in addr.split(",") if p.strip()]
    tokens = [
        t
        for t in re.findall(r"[A-Za-z0-9]+", f"{name} {addr}")
        if len(t) >= MIN_TOKEN and t.lower() not in GENERIC_WORDS
    ]
    return whole, tokens


@scorer(metrics=[accuracy()])
def no_leak():
    """GATE. No client_name / site_address (case-insensitive, address parts, word tokens >= 4 chars) in a request."""

    async def score(state: TaskState, target: Target) -> Score:
        whole, tokens = _terms(state.metadata["site"])
        leaks = []
        for body in state.metadata["recorded_requests"]:
            text = request_text(body)
            haystacks = (body.lower(), text.lower())
            leaks += [w for w in whole if any(w.lower() in h for h in haystacks)]
            # Tokens are matched outside <passage> blocks: public guidance text may contain words like "example".
            outside = PASSAGE_BLOCK.sub(" ", text).lower()
            leaks += [t for t in tokens if re.search(rf"\b{re.escape(t.lower())}\b", outside)]
        leaks = sorted(set(leaks))
        return Score(
            value=INCORRECT if leaks else CORRECT,
            answer=f"{len(leaks)} leak(s)",
            explanation=f"requests checked: {len(state.metadata['recorded_requests'])}; leaked terms: {leaks}",
        )

    return score


@scorer(metrics=[accuracy()])
def round_trip():
    """GATE (offline only). Originals restored exactly, no placeholder left, redactions > 0 and == placeholders sent."""

    async def score(state: TaskState, target: Target) -> Score:
        site, md = state.metadata["site"], state.output.completion
        problems = [f"missing after restore: {k}" for k in ("client_name", "site_address") if site[k] not in md]
        problems += [f"unrestored placeholder: {t}" for t in PLACEHOLDER.findall(md)]
        if state.metadata["redactions"] <= 0:
            problems.append("redactions == 0")
        n_sent = len(state.metadata["sent_placeholders"])
        if state.metadata["redactions"] != n_sent:
            problems.append(f"redactions {state.metadata['redactions']} != placeholders sent {n_sent}")
        return Score(
            value=INCORRECT if problems else CORRECT,
            answer=f"redactions={state.metadata['redactions']}",
            explanation="; ".join(problems) or "ok",
        )

    return score


@scorer(metrics=[accuracy()])
def redacted_something():
    """Real mode: the model is free to ignore placeholders, so only require that redaction happened."""

    async def score(state: TaskState, target: Target) -> Score:
        n = state.metadata["redactions"]
        return Score(value=CORRECT if n > 0 else INCORRECT, answer=f"redactions={n}")

    return score


@task
def pii_leak(real: bool = False, offline: bool = False):
    real, offline = (str(v).lower() in ("1", "true", "yes") for v in (real, offline))
    if real:
        require_key()
    from contaminated_land.paths import LANCEDB_DIR, SITES_YAML

    if not offline and not LANCEDB_DIR.exists():
        raise SystemExit(f"search index missing at {LANCEDB_DIR}: run ingest/build_index.py, or pass -T offline=true.")

    sites = {r["site_id"]: r for r in yaml.safe_load(SITES_YAML.read_text())}
    return Task(
        dataset=[
            Sample(id=sid, input=f"{sid} / {cs}", metadata={"site_id": sid, "criteria_set": cs, "site": sites[sid]})
            for sid, cs in DEMO_RUNS
        ],
        solver=draft_through_recorder(real, offline),
        scorer=[no_leak(), redacted_something()] if real else [no_leak(), round_trip()],
        model="mockllm/model",  # inspect's own model is unused; the model under test is behind the transport
        metadata={"real": real, "offline": offline},
    )
