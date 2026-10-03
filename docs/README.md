# Docs index

Status: draft, 2026-10-02. Docs only. No code yet.

Site Assessment Assistant is a Python MCP server for Claude. It searches public Australian contaminated-land guidance with page citations, screens synthetic lab results against assessment criteria in plain code, and drafts a cited results section behind a redaction guardrail.

| File | What it answers |
|---|---|
| [01-product-spec.md](01-product-spec.md) | What the demo is, for whom, the three tools, success criteria, non-goals |
| [02-architecture.md](02-architecture.md) | Components, directory layout, tool contracts, configuration, where data goes. **The contract the build lanes code against.** |
| [03-data.md](03-data.md) | Source documents and licences, criteria tables, synthetic lab data, ingest cache |
| [04-evaluation.md](04-evaluation.md) | Eval tasks, golden sets, scorers, pass thresholds, model comparison |
| [05-tech-stack.md](05-tech-stack.md) | Chosen libraries with verified versions, rejected options and why |
| [06-guardrails-security.md](06-guardrails-security.md) | Threat model, redaction design, stack risks, release checklist |
| [08-decisions.md](08-decisions.md) | Decision log (D1 to D11), each with its alternative and status |
| [09-build-plan.md](09-build-plan.md) | Spikes, parallel lanes with file ownership, order, acceptance checklist |
| [10-open-questions.md](10-open-questions.md) | What is still undecided, who answers it, what it blocks |

## Rules for these docs

- Change the contract in [02-architecture.md](02-architecture.md) first, then the code.
- No criterion value is written in docs. Values live in `data/criteria/` with a document and page reference.
- Anything not verified against a primary source is marked unverified.
- No em-dashes.
- `docs/private/` is gitignored and never published.
