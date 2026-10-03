"""Task 5: can a non-Claude model act as the MCP host? It gets user turns, calls the REAL server's tools over a real
stdio subprocess (`uv run site-assess`, inspect's native MCP client) and answers. Cases: evals/golden/agent_cases.yaml.

  export OPENROUTER_API_KEY=...     # for the model under test; the server reads its own key from .env for draft_section
  uv run --frozen --no-sync inspect eval evals/agent_tool_use.py --model openrouter/qwen/qwen3.5-flash-02-23 \
      --max-connections 2 --log-dir $LOGS/agent

Scorers (deterministic, no judge): tool_calls (per case CORRECT iff every expect_calls entry is matched by some
call in any turn, with equal args, and no forbid_tools tool was called; metadata holds calls per turn, missing,
forbidden, step count, tool errors) and tool_call_count (mean calls per case). Answer quality is graded by hand from
the transcripts (evals/extract_agent.py).
"""

import json
from pathlib import Path

import yaml
from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.model import ChatMessageAssistant, ChatMessageSystem, ChatMessageTool, ChatMessageUser, GenerateConfig
from inspect_ai.scorer import CORRECT, INCORRECT, Score, Target, accuracy, mean, scorer
from inspect_ai.solver import Generate, TaskState, solver
from inspect_ai.tool import mcp_server_stdio

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "evals" / "golden" / "agent_cases.yaml"
MAX_STEPS = 8  # generate calls per user turn
SYSTEM = (
    "You are an assistant for environmental scientists. You have tools for contaminated-land site assessment. "
    "Use them when relevant."
)


def turn_calls(messages) -> list[list[dict]]:
    """Tool calls per user turn: [[{name, args}, ...], ...]."""
    turns: list[list[dict]] = []
    for m in messages:
        if isinstance(m, ChatMessageUser):
            turns.append([])
        elif isinstance(m, ChatMessageAssistant) and m.tool_calls and turns:
            turns[-1] += [{"name": c.function, "args": c.arguments} for c in m.tool_calls]
    return turns


def _matches(call: dict, exp: dict) -> bool:
    return call["name"] == exp["tool"] and all(call["args"].get(k) == v for k, v in (exp.get("args") or {}).items())


@solver
def mcp_host():
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        server = mcp_server_stdio(command="uv", args=["--directory", str(ROOT), "run", "--frozen", "site-assess"])
        state.messages.insert(0, ChatMessageSystem(content=SYSTEM))
        async with server:  # one real stdio subprocess per sample
            state.tools = await server.tools()
            steps = []
            for i, turn in enumerate(state.metadata["turns"]):
                if i:
                    state.messages.append(ChatMessageUser(content=turn))
                n = 0
                while n < MAX_STEPS:
                    state = await generate(state, tool_calls="single")
                    n += 1
                    last = state.messages[-1]
                    if not (
                        isinstance(last, ChatMessageTool)
                        or (isinstance(last, ChatMessageAssistant) and last.tool_calls)
                    ):
                        break
                steps.append(n)
            state.metadata["steps"] = steps
        return state

    return solve


@scorer(metrics=[accuracy()])
def tool_calls():
    async def score(state: TaskState, target: Target) -> Score:
        by_turn = turn_calls(state.messages)
        calls = [c for t in by_turn for c in t]
        missing = [e for e in state.metadata["expect_calls"] if not any(_matches(c, e) for c in calls)]
        forbidden = [c for c in calls if c["name"] in state.metadata["forbid_tools"]]
        errors = [m.error.message for m in state.messages if isinstance(m, ChatMessageTool) and m.error]
        ok = not missing and not forbidden
        return Score(
            value=CORRECT if ok else INCORRECT,
            explanation=f"missing={json.dumps(missing)} forbidden={json.dumps(forbidden)}",
            metadata={
                "calls_by_turn": by_turn,
                "missing": missing,
                "forbidden": forbidden,
                "steps": state.metadata.get("steps"),
                "tool_error": bool(errors),
                "tool_errors": errors,
            },
        )

    return score


@scorer(metrics=[mean()])
def tool_call_count():
    async def score(state: TaskState, target: Target) -> Score:
        n = sum(len(t) for t in turn_calls(state.messages))
        return Score(value=n, explanation=f"{n} tool call(s)")

    return score


@task
def agent_tool_use():
    cases = yaml.safe_load(CASES.read_text())
    return Task(
        dataset=[
            Sample(
                id=c["id"],
                input=c["turns"][0],
                metadata={
                    "name": c["name"],
                    "turns": c["turns"],
                    "expect_calls": c.get("expect_calls") or [],
                    "forbid_tools": c.get("forbid_tools") or [],
                    "rubric": c["rubric"],
                },
            )
            for c in cases
        ],
        solver=mcp_host(),
        scorer=[tool_calls(), tool_call_count()],
        config=GenerateConfig(temperature=0, max_retries=4),
    )
