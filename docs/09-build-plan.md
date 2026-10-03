# Build plan

Status: draft, 2026-10-02. Target: 2 to 3 working days. Nothing is built yet.

## Day 0: spikes (first 2 hours, before any lane starts)

These decide whether the plan holds. Each one is a yes/no answer, written into [08-decisions.md](08-decisions.md).

1. FastMCP v4 runs a hello-world tool in Claude Desktop and Claude Code over stdio.
2. A FastMCP App (or ext-apps resource) renders a small HTML table in Claude Desktop. If not, drop MCP Apps and use text plus a README chart.
3. docling parses one guidance PDF on CPU with page numbers and tables intact.
4. One OpenRouter call with the chosen model id succeeds from Python.

## Parallel lanes

Each lane owns its files. Shared contracts live in [02-architecture.md](02-architecture.md). A lane that needs a contract change asks first.

| Lane | Owns | Depends on | Done when |
|---|---|---|---|
| A. Sources and retrieval | `ingest/`, `data/sources.yaml`, `src/contaminated_land/retrieval.py`, `data/cache/` | Spike 3 | `search_guidance` returns cited passages; a retrieval smoke test passes |
| B. Criteria and screening | `data/criteria/`, `data/lab/`, `src/contaminated_land/screening.py`, `src/contaminated_land/apps/`, `tests/test_screening.py` | Spike 2 for the App only | Every criteria row cites doc and page from a fetched source; screening unit tests pass |
| C. Drafting and guardrails | `src/contaminated_land/drafting.py`, `redact.py`, `llm.py`, `tests/test_redact.py`, `tests/test_citations.py` | Spike 4; uses A and B through their contracts | Redaction round-trips; invalid citations are rejected in tests |
| D. Evals | `evals/` | A, B, C contracts | Three tasks run and print scores for at least one model |
| E. Packaging and presentation | `pyproject.toml`, `README.md`, `demo/`, `.github/workflows/`, `server.py` | All lanes | Clean-machine setup works with one uv command; GIF recorded |

## Order

- Day 1: spikes, then A and B in parallel. C starts on redaction and the citation validator, which need no index.
- Day 2: C finishes drafting, D builds the eval sets, E wires `server.py` and CI.
- Day 3: run evals on both models, fix the worst failure, write README results, record GIF, run Agent Scan on the server.

## Acceptance checklist

- [ ] All unit tests pass in CI.
- [ ] Every criteria value in `data/criteria/` has a doc id and page that resolve to a fetched source.
- [ ] Eval results for at least one model are in the README, including failure cases.
- [ ] `.env` is not tracked; `.env.example` has names only.
- [ ] Agent Scan output is recorded in the README security section.
- [ ] README states: synthetic data, not a compliance tool, a qualified person must check output.
- [ ] No em-dashes in public docs.
