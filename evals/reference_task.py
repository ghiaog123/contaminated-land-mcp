"""Verified inspect_ai pattern (installed version). Lane D copies this.

A task whose solver calls plain Python (no LLM) and a custom scorer.
Run: uv run --frozen --no-sync inspect eval evals/reference_task.py --model mockllm/model
"""
from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import CORRECT, INCORRECT, Score, Target, accuracy, scorer
from inspect_ai.solver import Generate, TaskState, solver


@solver
def python_call():
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        state.output.completion = str(len(state.input_text))
        return state

    return solve


@scorer(metrics=[accuracy()])
def exact():
    async def score(state: TaskState, target: Target) -> Score:
        ok = state.output.completion == target.text
        return Score(value=CORRECT if ok else INCORRECT, answer=state.output.completion)

    return score


@task
def reference():
    return Task(dataset=[Sample(input="abc", target="3")], solver=python_call(), scorer=exact())
