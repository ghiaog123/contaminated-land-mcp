"""Task 1 (docs/04-evaluation.md): does search_guidance surface the gold page? No LLM.

Run:  uv run --frozen --no-sync inspect eval evals/retrieval_citation.py -T mode=hybrid   (or bm25 / vector)
Scorers: recall_at_5 (gold (doc_id, page) among the top 5) and reciprocal_rank (over the top 20).
"""

import json
from pathlib import Path

import yaml
from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import Score, Target, mean, scorer
from inspect_ai.solver import Generate, TaskState, solver

GOLDEN = Path(__file__).parent / "golden" / "retrieval.yaml"


def _samples() -> list[Sample]:
    items = yaml.safe_load(GOLDEN.read_text())["items"]
    return [
        Sample(
            id=it["id"],
            input=it["question"],
            target=json.dumps(it["gold"]),
            metadata={"kind": it["kind"], "gold": it["gold"], "derived_from": it["derived_from"]},
        )
        for it in items
    ]


@solver
def search(mode: str):
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        from site_assess import retrieval  # lazy: keeps `inspect list tasks` free of lancedb/embedding imports

        hits = retrieval.search(state.input_text, top_k=20, mode=mode)
        ends = retrieval.page_ends([h["chunk_id"] for h in hits])
        state.output.completion = json.dumps(
            [
                {"chunk_id": h["chunk_id"], "doc_id": h["doc_id"], "page": h["page"], "page_end": ends[h["chunk_id"]]}
                for h in hits
            ]
        )
        return state

    return solve


def _first_hit_rank(state: TaskState) -> int | None:
    """1-based rank of the first returned passage covering a gold (doc_id, page), else None.

    A chunk covers every page in [page, page_end]: HybridChunker can merge a table with the notes before it."""
    from site_assess.retrieval import covers_page

    gold = [(g["doc_id"], g["page"]) for g in state.metadata["gold"]]
    for i, h in enumerate(json.loads(state.output.completion), start=1):
        if any(h["doc_id"] == d and covers_page(h["page"], h["page_end"], p) for d, p in gold):
            return i
    return None


@scorer(metrics=[mean()])
def recall_at_5():
    async def score(state: TaskState, target: Target) -> Score:
        rank = _first_hit_rank(state)
        return Score(
            value=float(rank is not None and rank <= 5), answer=str(rank), explanation=f"first gold rank: {rank}"
        )

    return score


@scorer(metrics=[mean()])
def reciprocal_rank():
    async def score(state: TaskState, target: Target) -> Score:
        rank = _first_hit_rank(state)
        return Score(value=1 / rank if rank else 0.0, answer=str(rank), explanation=f"first gold rank: {rank}")

    return score


@task
def retrieval_citation(mode: str = "hybrid"):
    if mode not in ("hybrid", "bm25", "vector"):
        raise ValueError(f"mode must be hybrid|bm25|vector, got {mode!r}")
    return Task(
        dataset=_samples(),
        solver=search(mode),
        scorer=[recall_at_5(), reciprocal_rank()],
        model="mockllm/model",  # no LLM is called; this only satisfies inspect's model requirement
        metadata={"mode": mode},
    )
