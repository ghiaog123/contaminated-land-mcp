# Decisions log

Each entry: what was decided, the alternative, and why. Status is `decided` or `proposed` (proposed means the owner has not confirmed it).

## D1. MCP server framework: FastMCP v4. Status: decided (spike 1 passed 2026-10-02)

- **Alternative:** the official MCP Python SDK (modelcontextprotocol/python-sdk, v2.2.0, 2026-09-07, MIT).
- **Why FastMCP:** decorator-style tools with little boilerplate, and a built-in Apps feature for UI rendered in the chat, in Python. FastMCP v4.0.10, 2026-09-25, Apache-2.0.
- **Risk:** the FastMCP feature list was not verified from its release notes. Confirm Apps support and current MCP spec support in the first build hour. If either fails, switch to the official SDK. Server code is small, so switching is cheap.
- The scout lanes disagreed: the MCP lane recommended the official SDK, the packaging lane recommended FastMCP. This entry settles it, subject to the check above.

## D2. LLM access: OpenRouter. Status: decided

- **Decided by the owner:** server-side LLM calls go through OpenRouter (OpenAI-compatible API), with a DeepSeek model for cost.
- **Model id: `deepseek/deepseek-v4.1-flash`** ($0.30 in / $1.20 out per million tokens when chosen on 2026-10-02 and again at the last check on 2026-10-03; briefly $0.02 / $0.42 in between). At $0.30 / $1.20, `qwen/qwen3.5-flash-02-23` ($0.065 / $0.26) is about 4.6x cheaper on output; switching the default is an open owner decision. Decided by the owner on 2026-10-02. `deepseek/deepseek-v4-pro` ($0.21 / $0.42) was the cheaper alternative and was not chosen.
- **Local runs (2026-10-03):** the owner runs local evals on the free `stealth/space-bunny-alpha` ($0 / $0, image input, 1M context) through `SITE_ASSESS_MODEL` in `.env`; the code default stays DeepSeek. The OpenRouter catalog lists an expiry of 2026-10-05, after which `SITE_ASSESS_MODEL` must go back to DeepSeek. Stealth models may log prompts; the demo data is fictional and redacted, and the guidance documents are public. The Sonnet comparison below has not been run (cheap or free models only).
- **Recommendation, not decided:** use DeepSeek for development and bulk eval runs, and `anthropic/claude-sonnet-5.5` ($2 / $10) for the README demo and GIF. Publish eval scores for both. The target employer has standardised on Claude, so a demo that defaults to a different model reads as ignoring their stack.
- Only `draft_section` and the eval judge call this model. The chat model in Claude Desktop or Claude Code is always Claude, whatever this setting says.

## D3. Citations: own format plus validation, not provider-native. Status: proposed

- **Alternative:** Claude API `search_result` content blocks, which give native citations.
- **Why not:** it is a Claude API feature, and it is unverified whether it survives OpenRouter. It also does not exist for DeepSeek.
- **Instead:** the prompt requires `[chunk_id]` on every claim, and code validates each citation against the passages supplied. This works with any model, and the eval measures it directly.

## D4. Parsing: docling. Status: proposed

- **Alternatives:** marker (slow on CPU, model weight licence to check), MinerU (heavy, custom licence), pymupdf4llm (AGPL), unstructured (weaker tables).
- **Why:** best table structure plus page provenance, runs on CPU, MIT. Guidance documents are full of threshold tables, so table fidelity decides retrieval quality.
- **Cost:** first run downloads layout and table models (a few hundred MB) and parsing takes minutes. Parse once and cache.

## D5. Retrieval: LanceDB hybrid (vector + full-text, reciprocal rank fusion). Status: proposed

- **Alternatives:** bm25s alone, Chroma (no native hybrid in embedded mode), sqlite-vec (pre-1.0, manual fusion), graph RAG frameworks (LightRAG, GraphRAG: costly LLM indexing, lose table fidelity).
- **Why:** exact-term match matters for analyte names and criterion codes, semantic match matters for questions. One embedded file, no server.
- **Optional:** FlashRank reranking of the top 20, only if the eval shows it helps.

## D6. Numbers are computed by code, never by the model. Status: decided

- Screening is deterministic Python. The model only writes prose around numbers it was given, and the validator checks every number in the draft against the screening output.
- Reason: a model that compares 0.3 to 0.25 wrong once is enough to sink trust with a technical user base.

## D7. Evaluation: inspect_ai. Status: proposed

- **Alternatives:** promptfoo (Node toolchain), DeepEval (judge defaults to OpenAI), Ragas (no push since 2026-02-24), MCP-specific eval repos (all small and stale).
- **Why:** Python-first, supports tool-use and agent trajectories, model-graded and exact scorers, log viewer. MIT.
- **Unverified:** the current inspect_ai version (the releases API returned tags only) and its MCP tool support.

## D8. PII guardrail: Microsoft Presidio. Status: proposed

- **Alternatives:** LLM Guard (repo archived), Guardrails AI and NeMo Guardrails (heavy, aimed at chatbots), GLiNER (better name recall, needs torch).
- **Why:** well known, MIT, custom recognizers for site ids and addresses, small spaCy model keeps install light.

## D9. Tracing: Arize Phoenix + OpenInference, local. Status: proposed

- **Alternatives:** Langfuse (self-host needs Postgres, ClickHouse, Redis, S3), Logfire (SaaS backend only).
- **Why:** one process, local UI, nothing leaves the machine. That is consistent with the data story.
- **Unverified:** Phoenix licence (API reports NOASSERTION; check before naming it in the README).

## D10. No live hosting, no separate UI. Status: proposed

- Reviewers may not have time or an account, and a dead link is worse than none. The repo plus a GIF is the deliverable.
- MCP Apps provides the visual moment inside Claude Desktop. Rendering there is **unverified**. Claude Code does not render it. The text output must stand on its own.

## D11. Synthetic data only. Status: decided

- No real client or site data. Lab CSVs are generated and labelled synthetic. Criteria values come only from a fetched primary source with a page reference.
