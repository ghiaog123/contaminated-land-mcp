# Evals

inspect_ai tasks, one file per task, specified in [docs/04-evaluation.md](../docs/04-evaluation.md). The results table below is filled from the logs.

Run everything from the repo root with the frozen environment. Keep logs out of the repo (`--log-dir`).

```bash
LOGS=/tmp/contaminated-land-mcp-evals   # any directory outside the repo
alias ie='uv run --frozen --no-sync inspect eval'
uv run --frozen --no-sync inspect list tasks evals    # sanity check: every task loads
```

## Gates and targets

| Task | Kind | Pass line | Needs |
|---|---|---|---|
| `screening_exact` | GATE | 100% (any miss is a bug in code or expected file) | nothing |
| `pii_leak` | GATE | 0 leaks, round trip 100% | nothing offline; key for `-T real=true` |
| `retrieval_citation` | target | recall@5 >= 0.8 | built index |
| `draft_faithfulness` | reported | citation validity after validator 100% by construction; judge score has no gate | key, index |

## Commands

```bash
# 1. retrieval (no LLM). Needs the LanceDB index from ingest/build_index.py.
ie evals/retrieval_citation.py -T mode=hybrid --model mockllm/model --display plain --log-dir $LOGS
uv run --frozen --no-sync python evals/run_ablation.py --log-dir $LOGS   # bm25 / vector / hybrid table in one go

# 2. screening (no LLM, no key)
ie evals/screening_exact.py --model mockllm/model --display plain --log-dir $LOGS

# 3. draft faithfulness (real model). Exits with a clear message when OPENROUTER_API_KEY is unset.
export OPENROUTER_API_KEY=...                    # never commit it
export CONTAMINATED_LAND_JUDGE_MODEL=<openrouter id>   # optional; claim_support is skipped with a message if unset
ie evals/draft_faithfulness.py -T draft_model=deepseek/deepseek-v4.1-flash --model mockllm/model --display plain --log-dir $LOGS

# 4. PII leak
ie evals/pii_leak.py -T offline=true --model mockllm/model --display plain --log-dir $LOGS  # echo model + fixed passages, no key, no index
ie evals/pii_leak.py --model mockllm/model --display plain --log-dir $LOGS                  # echo model, real retrieval (needs index)
ie evals/pii_leak.py -T real=true --model mockllm/model --display plain --log-dir $LOGS     # recorded real OpenRouter traffic (needs key)

# 5. agent tool use (real model as MCP host; real `uv run contaminated-land-mcp` stdio subprocess per sample; no judge)
export OPENROUTER_API_KEY=...
ie evals/agent_tool_use.py --model openrouter/stealth/space-bunny-alpha --epochs 3 --max-connections 2 --retry-on-error 2 --display plain --log-dir $LOGS/agent
uv run --frozen --no-sync python evals/extract_agent.py $LOGS/agent $GRADING/agent   # one markdown packet per case/epoch + summary.md
```

`--model mockllm/model` only satisfies inspect: no task here asks inspect's model to generate. The model under
test sits behind `contaminated_land.llm`, and the judge in `draft_faithfulness` is a separate `get_model` call.

## What each task checks

- `pii_leak`: a recording `httpx` transport stores every request body sent to the provider. Scorer `no_leak`
  asserts no `client_name`, `site_address` or address component (case-insensitive, JSON-decoded) appears, and no
  name or address word token of 4+ characters appears outside quoted guidance passages. Two ordinary words that
  are part of the fictional client names ("sample", "fuel") are exempted as lone tokens (`GENERIC_WORDS`); the
  full-string checks still cover the names. Scorer `round_trip` (echo model) asserts the originals are restored
  exactly, no placeholder is left, and `redactions` equals the placeholders sent. Scope: the provider boundary
  only.
- `draft_faithfulness`: `citation_validity_raw` (model's first reply vs the passages it was shown),
  `citation_validity_final` (returned draft vs `DraftResult.citations`), `number_fidelity`, `validator_removals`,
  `retries_used`, `claim_support` (LLM judge on cited sentences, per-sentence verdicts in score metadata), and
  `facts_support` (the same judge checks every uncited prose sentence against the FACTS block, which closes the
  gap where uncited sentences escaped both checks). Use a judge model that differs from the drafting model and
  record both ids. Eval-only note: the judges receive the restored (unredacted) draft and FACTS. That is
  eval-only, on fictional data, and is not the MCP server path.
- `retrieval_citation`: recall@5 and MRR of the gold `(doc_id, page)`; a hit counts when the gold page falls in a
  chunk's `[page, page_end]`; `run_ablation.py` also splits by `table` vs `narrative` questions.
- `agent_tool_use`: the model under test (`--model openrouter/<id>`, temperature 0) acts as the MCP host. Cases in
  `golden/agent_cases.yaml` (turns, `expect_calls`, `forbid_tools`, manual `rubric`). Inspect's native MCP client
  starts `uv run contaminated-land-mcp` over stdio per sample; up to 8 generate steps per turn. Scorer `tool_calls` is
  deterministic: CORRECT iff every `expect_calls` entry is matched by some call (same tool, each listed arg equal)
  and no `forbid_tools` tool was called; metadata holds calls per turn, missing, forbidden, steps and tool errors.
  `tool_call_count` is the mean calls per case. Answer quality is NOT scored: `extract_agent.py` writes full
  transcripts for hand grading. A sample that errors at the provider (429, empty reply, bad tool-call JSON) shows as
  ERROR in the grid and is rerun, not counted against the model. `draft_section` calls the server's own drafting
  model with the key from `.env`, so a case that reaches it also spends that (cheap) drafting cost.

## Golden set

`golden/retrieval.yaml` was drafted by a coding agent reading the source PDFs before any retrieval output existed,
with `derived_from` per item. Gold is a location (1-based PDF page), never a criterion value. Do not edit an item to make a variant
pass; change it with a stated reason.

## Results table

Measured 2026-10-03, inspect_ai 0.3.275, 3 samples (DEMO-01/02/03), one draw
each, temperature 0. Cost = `input_tokens x input_price + output_tokens x output_price` from the log token counts;
re-check prices before publishing. Cells stay blank where nothing was measured. Judge for all
`draft_faithfulness` rows: `google/gemini-3.5-flash-lite` (provisional).

| Model | Task | Score | Cost (USD) | Latency (s, median) | Notes |
|---|---|---|---|---|---|
| (hybrid default) | retrieval_citation | recall@5 0.85, MRR 0.80 | n/a | | Index rebuilt: 1712 chunks (nepm-asc-b1 257, nepm-asc-b2 429, dwer-acs-2021 1026), build 370 s. Before the fixes: 0.85 / 0.76. bm25 0.90 / 0.72 (was 0.90 / 0.67), vector 0.85 / 0.75 (was 0.85 / 0.69). |
| n/a | screening_exact | 13 / 13 exact | n/a | | |
| deepseek/deepseek-v4.1-flash (run A, baseline prompt) | draft_faithfulness: citation validity (raw / after validator) | 1.0 / 1.0 | | | Removals 0; retries mean 0.33. Drafting tokens not logged. |
| deepseek/deepseek-v4.1-flash (run A) | draft_faithfulness: number fidelity | 1.0 | | | |
| deepseek/deepseek-v4.1-flash (run B, rule 2 rewritten) | draft_faithfulness: claim support | 1.0 (10 / 10) | about 0.0092 drafting + about 0.0012 judge | | 14,211 in / 21,182 out tokens, retries mean 0.33. |
| stealth/space-bunny-alpha (run C, final) | draft_faithfulness: citation validity (raw / after validator) | 1.0 / 1.0 | 0 (drafting) | 390 (wall, 3 concurrent samples) | Removals 0; retries 0. Drafting tokens 9,767 in / 34,009 out. Prompt adds rule 7 (at least one cited guidance sentence per exceeding analyte group) and rule 8 (recommendations and next steps must cite a passage or be left out); redaction fix and rebuilt index active. |
| stealth/space-bunny-alpha (run C) | draft_faithfulness: number fidelity | 1.0 | | | |
| stealth/space-bunny-alpha (run C) | draft_faithfulness: claim support | 0.933 | about 0.020 (judge) | | Judge tokens 65,953 in / 135 out. |
| offline echo model | pii_leak | no_leak 1.0, round_trip 1.0 | n/a | | |
| deepseek/deepseek-v4.1-flash (real mode) | pii_leak | no_leak 1.0, redacted_something 1.0 | | | |
| stealth/space-bunny-alpha (real mode) | pii_leak | no_leak 1.0, redacted_something 1.0 | 0 | | Stealth models may log prompts; the data is fictional and redacted. A grep of all eval logs for the key prefix found nothing. |
| stealth/space-bunny-alpha (manual-review rerun, 3 draws, no judge) | draft_faithfulness: citation validity / number fidelity | 1.0 / 1.0 / 1.0 over 9 draws | 0 | | Removals 0, retries 0. Graded by hand: cited sentences supported 54 / 56, uncited sentences supported by FACTS 124 / 127. |
| stealth/space-bunny-alpha (agent run 1, 3 draws) | agent_tool_use | tool_calls 36 / 36, mean 5.03 calls | 0 (agent); qwen smoke test about 0.0025 | | |
| stealth/space-bunny-alpha (agent run 2, 3 draws) | agent_tool_use | tool_calls 36 / 36, mean 4.31 calls, 0 step-cap hits | 0 | | Full passages and not-screened rows returned. |

Redaction in runs C and the real-mode pii_leak rows keeps sample ids such as FILL-02 and analyte names such as
"Mercury" and "BaP TEQ" readable: they are in the keep list, and an NER span inside a keep term is left alone. Only
the client name, address and site id are redacted.

OCR: not needed. The only low-text pages are nepm-asc-b2 pp.138 and 140-144 (figures: site plan, contour map,
borehole and well logs) and p150 (blank). No golden question targets them and docling lost no table text (checked
against the pypdf text layer). No vision model was used.
