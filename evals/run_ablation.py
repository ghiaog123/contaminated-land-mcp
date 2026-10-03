"""Run retrieval_citation for bm25, vector and hybrid on the same golden set and print one table.

  uv run --frozen --no-sync python evals/run_ablation.py [--log-dir DIR]

Needs the built index (ingest/build_index.py). Paste the table into the README; failures are published too.
"""

import argparse
import os
from pathlib import Path

from inspect_ai import eval

TASK = os.path.relpath(Path(__file__).parent / "retrieval_citation.py")  # inspect rejects absolute globs
MODES = ["bm25", "vector", "hybrid"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--log-dir", default="logs", help="inspect log directory (keep it out of the repo)")
    args = ap.parse_args()

    rows = []
    for mode in MODES:
        log = eval(TASK, task_args={"mode": mode}, log_dir=args.log_dir, display="none")[0]
        if log.status != "success" or not log.samples:
            rows.append((mode, f"FAILED ({log.status}): {log.error.message if log.error else 'no samples'}"))
            continue
        by_kind: dict[str, list[float]] = {}
        rr, hit = [], []
        for s in log.samples:
            hit.append(s.scores["recall_at_5"].value)
            rr.append(s.scores["reciprocal_rank"].value)
            by_kind.setdefault(s.metadata["kind"], []).append(s.scores["recall_at_5"].value)
        avg = lambda xs: sum(xs) / len(xs)  # noqa: E731
        rows.append(
            (
                mode,
                f"{avg(hit):.2f}",
                f"{avg(rr):.2f}",
                f"{avg(by_kind.get('table', [0])):.2f}",
                f"{avg(by_kind.get('narrative', [0])):.2f}",
                str(len(hit)),
            )
        )

    print("\n| mode | recall@5 | MRR | recall@5 table | recall@5 narrative | n |\n|---|---|---|---|---|---|")
    for r in rows:
        print("| " + " | ".join(r) + " |" if len(r) > 2 else f"| {r[0]} | {r[1]} |")


if __name__ == "__main__":
    main()
