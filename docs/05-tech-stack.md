# Tech stack

Status: draft, 2026-10-02. Versions, dates, licences and star counts were read from the GitHub API on 2026-10-02 unless marked unverified. Reasoning lives in [08-decisions.md](08-decisions.md); this file lists what was chosen and what was rejected.

## Chosen

| Component | Choice | Version / date | Licence | Stars | Role in demo | Decision |
|---|---|---|---|---|---|---|
| MCP server framework | FastMCP (PrefectHQ/fastmcp) | v4.0.10, 2026-09-25 | Apache-2.0 | 28.0k | Tool registration, stdio transport. Alternative: official `modelcontextprotocol/python-sdk` v2.2.0, 2026-09-07, MIT, 24.4k | [D1](08-decisions.md) |
| MCP debugging | MCP Inspector (modelcontextprotocol/inspector) | 2.9.0, 2026-09-30 | unverified | 11.0k | Debug and demo tools via `npx` | none |
| MCP Apps | modelcontextprotocol/ext-apps | v2.0.3, 2026-09-25 | Apache-2.0 per its LICENSE file (API reports NOASSERTION) | 2.9k | `ui://` resource for the exceedance table. Per its docs it renders in Claude web and Desktop; Claude Code is not listed. Rendering in our setup is unverified | [D10](08-decisions.md) |
| Desktop packaging | MCPB (modelcontextprotocol/mcpb) | v2.1.2, 2025-12-04 | unverified | 2.1k | Optional one-click Claude Desktop install. Last release is 10 months old | none |
| PDF parsing | docling (docling-project/docling) | v2.132.0, 2026-10-01 | MIT | 68.3k | Parse guidance PDFs with tables and page provenance, on CPU | [D4](08-decisions.md) |
| Chunking | docling-core `HybridChunker` | v2.99.0 | unverified | n/a | Structure-aware chunks, keeps table context | [D4](08-decisions.md) |
| Index and retrieval | LanceDB (lancedb/lancedb) | v0.39.0, 2026-09-17 | Apache-2.0 | 11.6k | Embedded vector + full-text index, hybrid search with RRF | [D5](08-decisions.md) |
| Retrieval fallback | bm25s (xhluca/bm25s) | 0.3.11 | MIT | 1.8k | Only if LanceDB FTS fails the smoke test | [D5](08-decisions.md) |
| Embeddings | fastembed 0.8.1 with `BAAI/bge-small-en-v1.5` (384-d) | chosen and built 2026-10-02 | unverified | n/a | Local embeddings, no API call | [D5](08-decisions.md) |
| Reranker (optional) | FlashRank | 0.2.9, 2024-11-29 | Apache-2.0 | 1.0k | Rerank top 20, only if the eval shows a gain | [D5](08-decisions.md) |
| Server-side LLM | OpenRouter, OpenAI-compatible API | n/a | n/a (service) | n/a | `draft_section` and the eval judge. Default model `deepseek/deepseek-v4.1-flash` | [D2](08-decisions.md) |
| Evaluation | inspect_ai (UKGovernmentBEIS/inspect_ai) | 0.3.275 (installed 2026-10-02) | MIT | 2.9k | Retrieval, screening and drafting evals | [D7](08-decisions.md) |
| PII redaction | Presidio (microsoft/presidio) with spaCy `en_core_web_sm` | 2.2.364, 2026-07-22 | MIT | 11.1k | Redact before the OpenRouter call, custom recognizers | [D8](08-decisions.md) |
| Tracing | Arize Phoenix (Arize-ai/phoenix) + OpenInference | Phoenix v20.19.0, 2026-10-01 | Phoenix unverified (likely Elastic 2.0); OpenInference Apache-2.0 | 11.7k | Local trace UI | [D9](08-decisions.md) |
| Packaging and lint | uv (astral-sh/uv) | 0.12.22, 2026-10-02 | Apache-2.0 | 90.4k | Env, lockfile, one-command setup | none |
| Lint | ruff | 0.16.10 | MIT | n/a | Lint and format | none |
| Type check (optional) | ty | 0.0.84 | unverified | n/a | Non-blocking in CI | none |
| README GIF | vhs (charmbracelet/vhs) | v0.12.1, 2026-09-24 | MIT | 21.0k | Scripted terminal recording | none |
| README chart | matplotlib or altair | unverified | unverified | n/a | Static eval chart | none |
| Server security scan | Agent Scan (snyk/agent-scan, formerly invariantlabs mcp-scan) | v0.6.8, 2026-09-29 | Apache-2.0 | 3.1k | Scan our own server, record output in README. 0.x release | [06](06-guardrails-security.md) |

## LLM options on OpenRouter

Prices per million tokens, input / output, re-read from the OpenRouter catalog 2026-10-03. DeepSeek v4.1-flash moved twice: $0.30 / $1.20 on 2026-10-02, $0.02 / $0.42 early on 2026-10-03, $0.30 / $1.20 again later on 2026-10-03. Default for `draft_section`: `deepseek/deepseek-v4.1-flash` ([D2](08-decisions.md)).

| OpenRouter id | In / out (USD) |
|---|---|
| `deepseek/deepseek-v4.1-flash` | 0.30 / 1.20 at the last check (image input supported); see the note above |
| `stealth/space-bunny-alpha` | 0 / 0 (image input, 1M context). Used by the owner for local runs via `CONTAMINATED_LAND_MODEL` in `.env`. The catalog lists an expiry of 2026-10-05; after that `CONTAMINATED_LAND_MODEL` must go back to DeepSeek. Stealth models may log prompts; the demo data is fictional and redacted and the guidance documents are public |
| `google/gemini-3.5-flash-lite` | 0.30 / 2.50. Eval judge, provisional |
| `deepseek/deepseek-v4-pro` | 0.21 / 0.42 |
| `deepseek/deepseek-v4-flash` | 0.028 / 0.056 |
| `anthropic/claude-sonnet-5.5` | 2 / 10 |
| `anthropic/claude-haiku-4.5` | 1 / 5 |

Claude model ids current on 2026-10-02 (Anthropic naming): `claude-fable-5-1`, `claude-opus-5-5`, `claude-sonnet-5-5`, `claude-haiku-4-5`. OpenRouter naming differs, for example `anthropic/claude-sonnet-5.5`. Use the OpenRouter form in `CONTAMINATED_LAND_MODEL`.

## Rejected

| Name | Reason |
|---|---|
| marker | Slow on CPU; weight licence to check |
| MinerU | Heavy; custom licence |
| unstructured | Weak tables; large dependencies |
| pymupdf4llm | AGPL |
| olmOCR, ColPali | Need a GPU |
| LightRAG, GraphRAG | LLM indexing cost; lose table fidelity |
| RAGFlow | Docker stack; release candidates only |
| txtai | Hides the pipeline we want to show |
| Chroma | No native embedded hybrid search |
| Qdrant local mode | No gain over LanceDB here |
| chonkie | Redundant with `HybridChunker` |
| Ragas | No push since 2026-02-24 |
| LLM Guard | Repo archived |
| Guardrails AI, NeMo Guardrails | Heavy; aimed at chatbots |
| Logfire | SaaS-only backend |
| Langfuse self-host | Needs Postgres, ClickHouse, Redis and S3 |
| MCP-specific eval repos | All 134 stars or fewer, stale |
| mcp-ui | Superseded by MCP Apps |
| Live hosting | Dead-link risk ([D10](08-decisions.md)) |
| Claude API `search_result` citations | Claude-only; unverified through OpenRouter ([D3](08-decisions.md)) |

## Pinning policy

- Pin exact versions in `uv.lock` and commit it.
- Re-verify every row above at build start (version, licence, whether the repo is still maintained) and record the date in this file.
- Rows marked unverified must be resolved before they are named in the README.
- The MCP spec and Python SDK are moving fast; see [06-guardrails-security.md](06-guardrails-security.md#4-stack-risks).
