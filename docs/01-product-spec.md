# Product spec: Site Assessment Assistant

Status: draft, 2026-10-02. Docs only. No code yet.

## Problem

Environmental consultancies that assess contaminated land spend large amounts of senior time on three things:

1. **Lab results handling.** Lab certificates and field records need days of manual handling before anyone can analyse them. The core analysis step compares each analyte result against published assessment criteria (for example the health investigation and screening levels in the Australian NEPM).
2. **Finding guidance.** Thousands of pages of standards, guidelines and past reports. The same question gets answered from scratch because nobody can search them properly.
3. **Regulatory reporting.** Report formats are rigid but the content is not. Drafting a results section takes senior people days.

## What this demo is

An MCP server written in Python that gives Claude three tools, one for each problem above. It runs locally from Claude Desktop or Claude Code. It uses only public guidance documents and synthetic lab data.

It is a portfolio demo, not a product. The goal is to show working retrieval, tool use, deterministic calculation, evaluation and data guardrails in a domain a contaminated-land consultancy recognises at once.

## Users (as imagined for the demo)

- **Environmental scientist / engineer.** Technical, not a software person. Wants a correct answer with a page reference they can check, not a chatbot opinion.
- **Senior reviewer.** Signs off reports. Cares that every number traces to a source and that client data does not leak.

## Tools

| Tool | Problem | Behaviour | Who computes |
|---|---|---|---|
| `search_guidance` | Finding guidance | Hybrid search over parsed guidance PDFs. Returns ranked passages, each with document id, title and page. | Code (retrieval). No LLM call. |
| `screen_lab_results` | Lab results | Reads a lab results CSV, matches each analyte to the selected assessment criteria, returns every exceedance with the criterion value and its source page. | Code only. **The LLM never compares numbers.** |
| `draft_section` | Reporting | Builds a "Results and discussion" section for one site from the screening output plus retrieved guidance. Every claim carries a `[doc_id p.N]` citation that the server validates before returning. | LLM (server-side call), wrapped by redaction and citation validation. |

Full input and output contracts: [02-architecture.md](02-architecture.md#tool-contracts).

## Demo flow (what the README GIF shows)

1. User in Claude: "Screen the results for site DEMO-01 against residential criteria."
2. Claude calls `screen_lab_results`. A table of exceedances appears, inline as an MCP App where the host supports it, as text otherwise.
3. User: "What does the guidance say about the exceedances?" Claude calls `search_guidance` and answers with page citations.
4. User: "Draft the results section." Claude calls `draft_section` and returns a cited draft.

## Success criteria

- Every number in a screening result is reproducible from the CSV and the criteria table. Covered by unit tests.
- Every citation in a `draft_section` output resolves to a real chunk. Invalid citations are rejected, not shown.
- No client name or site address from the input reaches the model provider in clear text. Covered by an eval.
- Setup from a clean machine is one `uv` command plus an API key.
- Eval scores are published in the README, including where the system fails.

## Non-goals

- No web UI. Claude is the UI.
- No live hosting. A broken live link is worse than none.
- No graph RAG, no GPU models, no vector database server.
- No real client data, ever. Synthetic data only.
- Not a compliance tool. Output is a draft for a qualified person to check. The README says so.

## Open questions

See [10-open-questions.md](10-open-questions.md).
