# Guardrails and security

Status: draft, 2026-10-02. Describes the controls the demo is built against. Nothing is built yet, so every control below is a design target until its test exists.

## 1. Threat model

| Threat | Example | Control | Test |
|---|---|---|---|
| Client identifiers reach the OpenRouter model provider | A client name or site address in `sites.yaml` ends up in the prompt | Presidio redaction before the LLM call, with a reversible placeholder map kept in server memory; custom recognizers for site ids and addresses ([D8](08-decisions.md)) | `pii_leak` eval in [04-evaluation.md](04-evaluation.md); redaction round-trip unit test |
| Prompt injection via PDF or guidance text | A passage says "ignore previous instructions and ..." | Passages are untrusted data: delimited in the prompt, never executed as instructions; tool outputs carry no instructions | Optional injection eval (planted instruction in a test passage) |
| Tool poisoning or malicious tool descriptions | A third-party MCP server hides instructions in a tool description | The demo exposes only our own server and three tools; scan it with Agent Scan and record the run in the README | Agent Scan output in README |
| Hallucinated citations or numbers | Draft cites a `chunk_id` that was not supplied, or restates 0.3 as 0.03 | Citation validator plus number-fidelity check against screening output; failing sentences removed and listed in `warnings` ([D3](08-decisions.md), [D6](08-decisions.md)) | `tests/test_citations.py`; citation and number evals |
| Secrets leak | API key committed or logged | `.env` gitignored; `.env.example` has names only; key never logged | Release checklist (section 5); trace inspection shows no key |
| Traces contain data | Phoenix spans hold prompts with lab values | Phoenix runs locally only, tracing off unless `PHOENIX_COLLECTOR_ENDPOINT` is set ([D9](08-decisions.md)); traces must not contain the key | Inspect a trace before release |
| Model provider data residency | OpenRouter routes to third-party providers; DeepSeek models may be served by providers in various jurisdictions | Check OpenRouter provider routing and data policies; pin providers where the option exists. Real client data would need a provider under a data agreement. That is a deployment requirement; the demo uses synthetic data only ([D11](08-decisions.md)) and does not solve it | Documented; not testable in the demo |
| Over-trust by users | Draft is treated as a finished, compliant report | README and every draft state: draft only, a qualified person must check, not a compliance tool | Draft template check; README review |

## 2. Data flow

The table of what leaves the machine, and to whom, is in [02-architecture.md, "Where data goes"](02-architecture.md#where-data-goes). It is not repeated here.

One caveat governs everything: whatever a tool returns is read by the host model, which is always Claude (Anthropic) in Claude Desktop and Claude Code. Redaction protects the OpenRouter hop only. `draft_section` restores placeholders in its returned draft, so client identifiers do reach the host. Keeping them from the host too would need a separate local restore step. That is out of scope for the demo and stated in the README.

## 3. Redaction design

| Item | Design |
|---|---|
| Entities | `PERSON`, `ORG` (client), `LOCATION` / address, custom `SITE_ID` |
| Sources | Names and addresses from `data/lab/sites.yaml` (exact match, high confidence) plus Presidio NER over the rest of the prompt text |
| Placeholder format | Typed and numbered, for example `<CLIENT_1>`, `<ADDRESS_1>`, `<SITE_1>`. Same value gets the same placeholder within a request |
| Map lifetime | One request, in server memory only. Never written to disk, logs or traces |
| Restore | After citation validation, placeholders in the draft are swapped back |
| Reporting | `redactions` in the output is a count only, never the values |
| Round-trip test | Redact, then restore, must equal the original for every fixture site |
| Leak test | `pii_leak` eval greps the outgoing prompt, as captured at the HTTP client, for every configured identifier |

Known limits:

- NER misses names and addresses in unusual forms. The `sites.yaml` exact-match pass is the main defence, not the model.
- False positives happen (a place name inside a guidance title is redacted). The cost is a slightly worse prompt.
- Numbers are not redacted by design: the draft needs them, and screening values are synthetic here.
- Redaction does not remove information inferable from context, such as an unusual analyte mix.

## 4. Stack risks

Stated openly. Also the answer to "what is wrong or risky about a Claude + MCP stack".

| Risk | Detail |
|---|---|
| MCP spec churn | Spec revision 2026-07-28 is breaking: stateless protocol (initialize handshake, `Mcp-Session-Id` and SSE resumability removed, `server/discover` added); tasks moved to the extension `io.modelcontextprotocol/tasks`; sampling and roots deprecated; dynamic client registration replaced by Client ID Metadata Documents. Python SDK 2.2.0 still lists tasks as not implemented. |
| Which revision the host speaks | Which spec revision Claude Desktop and Claude Code negotiate is unverified. Assume 2025-11-25 behaviour. Mitigation: pin versions ([05-tech-stack.md](05-tech-stack.md#pinning-policy)) and keep the server thin so a framework swap is cheap ([D1](08-decisions.md)). |
| MCP Apps is host-dependent | Rendering depends on the host. Claude Code does not render it. Text output must stand alone ([D10](08-decisions.md)). |
| 0.x tooling | Agent Scan (v0.6.8) and the Agent SDK are 0.x; behaviour and output may change. |
| Prompt injection | Unsolved in general. The controls above reduce exposure; they do not eliminate it. |
| Single-vendor dependence | The host model is always Claude. The server cannot change that, and everything a tool returns goes to it. |
| Cost and rate limits | `draft_section` makes server-side LLM calls (plus one retry on validation failure). Per-call cost depends on the model ([model prices](05-tech-stack.md#llm-options-on-openrouter)); OpenRouter and provider rate limits apply. Evals multiply the cost. |

## 5. Security checklist for release

- [ ] `git ls-files` shows no `.env`; `.env.example` has variable names only.
- [ ] Search history and tree for the API key prefix and for any real-looking client name or address: none found.
- [ ] `pii_leak` eval passes; redaction round-trip test passes.
- [ ] Citation and number-fidelity tests pass; invalid citations are rejected, not shown.
- [ ] Optional injection eval run, result recorded in README including failures.
- [ ] Agent Scan run against the server; output recorded in README.
- [ ] A Phoenix trace was inspected: no API key, no unredacted identifiers in the outbound LLM span.
- [ ] Logs checked: key and placeholder map never printed.
- [ ] `uv.lock` committed; dependency versions re-verified and dated in [05-tech-stack.md](05-tech-stack.md).
- [ ] OpenRouter provider routing and data policy for the chosen model reviewed; result noted in README.
- [ ] README states: synthetic data only, not a compliance tool, a qualified person must check all output.
- [ ] Every `data/sources.yaml` entry has a licence and retrieved date; criteria values cite doc and page.
- [ ] No em-dashes in public docs.
