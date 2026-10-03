"""screening_exact: no LLM. Runs contaminated_land.screening.screen
over hand-computed fixtures in evals/golden/screening/.

Each case folder holds sites.yaml, <site_id>.csv, expected.json and WORKING.md (the hand calculation).
Scoring is exact: set of (sample_id, analyte) exceedances, ratio per exceedance, set of (sample_id, analyte, reason)
not_screened, plus determinism (two runs serialise byte-identically). Any miss is a bug in the code or the expected
file; investigate before changing either.

Run: uv run --frozen --no-sync inspect eval evals/screening_exact.py --model mockllm/model
"""
import inspect
import json
from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import CORRECT, INCORRECT, Score, Target, accuracy, scorer
from inspect_ai.solver import Generate, TaskState, solver

from contaminated_land import screening

GOLDEN = Path(__file__).parent / "golden" / "screening"


def _clear_caches() -> None:
    for obj in vars(screening).values():
        if hasattr(obj, "cache_clear"):
            obj.cache_clear()


def _screen_case(case: Path, site_id: str, criteria_set: str) -> str:
    """Point screening at the fixture folder, run once, return the canonical JSON text."""
    old = screening.LAB_DIR, screening.SITES_YAML
    screening.LAB_DIR, screening.SITES_YAML = case, case / "sites.yaml"
    _clear_caches()
    try:
        out = screening.screen(site_id, criteria_set)
        if inspect.isawaitable(out):
            raise TypeError("screen() returned an awaitable; this eval expects a sync function")
        return json.dumps(out, sort_keys=True)
    finally:
        screening.LAB_DIR, screening.SITES_YAML = old
        _clear_caches()


@solver
def run_screening():
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        case = GOLDEN / state.input_text
        expected = json.loads((case / "expected.json").read_text())
        site_id = next(case.glob("*.csv")).stem
        try:
            first = _screen_case(case, site_id, expected["criteria_set"])
            second = _screen_case(case, site_id, expected["criteria_set"])
            state.metadata.update(actual=first, deterministic=first == second)
        except Exception as e:  # a crash is a failed case, not a crashed eval
            state.metadata.update(actual=None, error=f"{type(e).__name__}: {e}")
        state.output.completion = state.input_text
        return state

    return solve


def _diff(label: str, want: dict, got: dict) -> list[str]:
    lines = [f"{label} missing: {k} {want[k]}" for k in sorted(want.keys() - got.keys())]
    lines += [f"{label} unexpected: {k} {got[k]}" for k in sorted(got.keys() - want.keys())]
    shared = sorted(want.keys() & got.keys())
    lines += [f"{label} {k}: want {want[k]} got {got[k]}" for k in shared if want[k] != got[k]]
    return lines


@scorer(metrics=[accuracy()])
def exact_screening():
    async def score(state: TaskState, target: Target) -> Score:
        if state.metadata.get("actual") is None:
            return Score(value=INCORRECT, explanation=f"{target.text}: {state.metadata.get('error')}")
        got = json.loads(state.metadata["actual"])
        want = json.loads((GOLDEN / target.text / "expected.json").read_text())
        problems = []
        if got.get("criteria_set") != want["criteria_set"]:
            problems.append(f"criteria_set: want {want['criteria_set']} got {got.get('criteria_set')}")
        # dict keyed by (sample, analyte); a repeated key in a list would be a duplicate-report bug
        for label, rows in (("exceedances", got["exceedances"]), ("not_screened", got["not_screened"])):
            keys = [(r["sample_id"], r["analyte"]) for r in rows]
            if len(keys) != len(set(keys)):
                problems.append(f"{label} contains a repeated (sample_id, analyte)")
        problems += _diff("exceedance(ratio)",
                          {(e["sample_id"], e["analyte"]): e["ratio"] for e in want["exceedances"]},
                          {(e["sample_id"], e["analyte"]): e["ratio"] for e in got["exceedances"]})
        problems += _diff("not_screened(reason)",
                          {(n["sample_id"], n["analyte"]): n["reason"] for n in want["not_screened"]},
                          {(n["sample_id"], n["analyte"]): n["reason"] for n in got["not_screened"]})
        if not state.metadata["deterministic"]:
            problems.append("two runs were not byte-identical")
        return Score(value=INCORRECT if problems else CORRECT, answer=target.text,
                     explanation=f"{target.text}: " + ("OK" if not problems else "; ".join(problems)))

    return score


@task
def screening_exact():
    cases = sorted(p.name for p in GOLDEN.iterdir() if (p / "expected.json").exists())
    return Task(dataset=[Sample(input=c, target=c, id=c) for c in cases],
                solver=run_screening(), scorer=exact_screening())
