# Open questions

Status: draft, 2026-10-02. Each question names who answers it and what it blocks. When answered, move the answer into [08-decisions.md](08-decisions.md) and delete the row.

| # | Question | Answered by | Blocks |
|---|---|---|---|
| Q2 | Does the README demo and GIF default to `anthropic/claude-sonnet-5.5`, with DeepSeek for development and bulk evals? Recommended in [D2](08-decisions.md#d2-llm-access-openrouter-status-decided). | Owner | Lane E README, eval results table. Open as of 2026-10-03: the Sonnet comparison was not run because the owner chose cheap or free models only |
| Q3 | `OPENROUTER_API_KEY`: not available yet (2026-10-02); the owner will provide it. It goes in `.env` (gitignored), never into chat or a committed file. | Owner | Spike 4, everything that calls the LLM: `draft_section`, evals 3 and 4 |
| Q5 | Does an MCP App render in Claude Desktop today? | Spike 2 | Lane B `apps/`, the README GIF |
| Q6 | Which source documents may be redistributed in the repo, and which must be fetched at install time? | Lane A, from each licence | [03-data.md](03-data.md), `data/cache/` policy |
| Q7 | Which `criteria_set` ids ship in the demo (land-use scenarios, soil types, depth bands)? | Lane B | Synthetic lab data design, eval golden sets |
| Q8 | GitHub account and repo name for publishing (default `site-assessment-mcp`), and licence for the repo code (default MIT). | Owner | Lane E, publishing |
| Q10 | Phoenix licence (API reports NOASSERTION) before naming it in the README. | Lane E | README tracing section |
| Q12 | Which judge model for `SITE_ASSESS_JUDGE_MODEL`? A judge from a different family than the drafting model avoids self-grading. Provisionally answered 2026-10-03: `google/gemini-3.5-flash-lite` (different family from the drafter, and cheap); owner to confirm. | Owner | `draft_faithfulness` task |
| Q13 | Confirm screening semantics proposed in [03-data.md](03-data.md): exceedance is strictly `result > criterion`, below-LOR rows go to `not_screened`, duplicates are screened as separate samples. | Owner | Lane B tests, `screening_exact` golden set |
| Q14 | Confirm eval gates proposed in [04-evaluation.md](04-evaluation.md): `screening_exact` 100% and `pii_leak` 0 leaks are hard gates; recall@5 >= 0.8 is a target; judge scores have no gate. | Owner | Lane D |
| Q15 | NEPM licence on legislation.gov.au is unverified. The DWER guideline is not openly licensed (reproduction unaltered, personal or in-organisation use only), so it is fetched at install time and never committed. | Lane A | `redistributable` flags in `data/sources.yaml` |

## Answered during the build (2026-10-02)

- Q4: FastMCP 4.0.10 supports MCP Apps (`AppConfig(resource_uri="ui://...")` sets `meta.ui.resourceUri`; the `ui://` resource is served). Verified in memory by `tests/test_fastmcp_reference.py` and `tests/test_server.py`. Rendering in Claude Desktop is still Q5.
- Q9: inspect_ai 0.3.275 runs plain-Python solvers and custom scorers (`evals/reference_task.py`). Its MCP tool support is not used: tasks call the Python functions behind the tools.
- Q11: embeddings are fastembed `BAAI/bge-small-en-v1.5` (384 dimensions), local, CPU.
