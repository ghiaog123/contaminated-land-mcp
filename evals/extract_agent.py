"""Turn agent_tool_use .eval logs into one markdown packet per (model, case, epoch) plus summary.md, for manual grading.

  uv run --frozen --no-sync python evals/extract_agent.py LOG_DIR OUT_DIR

When a (model, case, epoch) appears in several logs (a rerun after a provider error), the newest log wins unless it
errored and an older one did not. Samples with an error are marked ERROR, not INCORRECT: a provider error is not a
verdict on the model or the server.
"""

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

from inspect_ai.log import list_eval_logs, read_eval_log
from inspect_ai.model import ChatMessageAssistant, ChatMessageTool


def verdict(s) -> str:
    if s.error:
        return "ERROR"
    sc = (s.scores or {}).get("tool_calls")
    return "PASS" if sc and sc.value == "C" else "FAIL"


def packet(model: str, s) -> str:
    sc = (s.scores or {}).get("tool_calls")
    md = sc.metadata if sc else {}
    out = [
        f"# {s.id} ({s.metadata['name']}) | {model} | epoch {s.epoch}",
        f"\n**Deterministic verdict: {verdict(s)}**  \nmissing: {md.get('missing')}  "
        f"\nforbidden: {md.get('forbidden')}  "
        f"\nsteps per turn: {md.get('steps')}  \ntool error: {md.get('tool_error')} {md.get('tool_errors') or ''}",
        f"\nSample error: {s.error.message[:500] if s.error else 'none'}",
        f"\n**Rubric (manual grader):** {s.metadata['rubric']}",
    ]
    turn = 0
    for m in s.messages:
        if m.role == "system":
            continue
        if m.role == "user":
            turn += 1
            out.append(f"\n## Turn {turn}\n\n**USER:** {m.text}")
        elif isinstance(m, ChatMessageAssistant):
            if m.text.strip():
                out.append(f"\n**ASSISTANT:**\n\n{m.text}")
            for c in m.tool_calls or []:
                out.append(f"\n**TOOL CALL:** `{c.function}` {json.dumps(c.arguments)}")
        elif isinstance(m, ChatMessageTool):
            body = m.text or (m.error.message if m.error else "")
            out.append(f"\n**TOOL RESULT** (`{m.function}`{', ERROR' if m.error else ''}):\n\n```\n{body}\n```")
    return "\n".join(out) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("log_dir")
    ap.add_argument("out_dir")
    a = ap.parse_args()
    best: dict[tuple, tuple] = {}  # (model, case, epoch) -> (model, sample)
    for info in sorted(list_eval_logs(a.log_dir), key=lambda i: i.mtime or 0):  # oldest first
        log = read_eval_log(info.name)
        if log.eval.task != "agent_tool_use":
            continue
        for s in log.samples or []:
            key = (log.eval.model, str(s.id), s.epoch)
            if key not in best or not s.error or best[key][1].error:
                best[key] = (log.eval.model, s)
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    grid: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for (model, case, epoch), (_, s) in sorted(best.items()):
        (out / f"{re.sub(r'[^A-Za-z0-9.-]+', '_', model)}__{case}__e{epoch}.md").write_text(packet(model, s))
        grid[model][case].append(verdict(s))
    lines = ["# Agent tool-use: deterministic verdicts (PASS / FAIL / ERROR = provider or runtime error)\n"]
    for model, cases in grid.items():
        n = max(len(v) for v in cases.values())
        lines += [
            f"\n## {model}\n",
            "| case | " + " | ".join(f"e{i + 1}" for i in range(n)) + " |",
            "|---" * (n + 1) + "|",
        ]
        lines += [f"| {c} | " + " | ".join(v) + " |" for c, v in sorted(cases.items())]
    (out / "summary.md").write_text("\n".join(lines) + "\n")
    print(f"{len(best)} packets -> {out}")


if __name__ == "__main__":
    main()
