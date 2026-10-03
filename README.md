# Site Assessment Assistant

An MCP server that gives Claude three tools for contaminated-land site assessment: cited search over public Australian guidance (NEPM), lab-result screening against assessment criteria done in plain code, and a cited draft of a results section with client details redacted before any outside model sees them. Everything runs locally from Claude Desktop or Claude Code on public documents and synthetic lab data. It is a portfolio demo, not a product, and it is not a compliance tool: it produces drafts for a qualified person to check.

<img src="demo/demo-video.gif" width="480" alt="Walkthrough: the host model calls the four tools over MCP; only draft_section calls a model">

*A three-turn run on DEMO-03, replayed from a real agent transcript (eval case a09): screen, search the guidance, draft. Only `draft_section` calls a model: client names are swapped for placeholders before it, and citations and numbers are checked after it. Every value on screen comes from `demo/video/data.json`, which names its sources. [MP4](demo/demo.mp4), rendered with `uv run --with playwright python demo/video/render.py`.*

![Demo: screening DEMO-03 and searching the guidance](demo/demo.gif)

*Terminal demo of `screen_lab_results` and `search_guidance`, rendered from `demo/demo.tape` with vhs. The Claude Desktop recording (with `draft_section` and the inline table) is manual and not recorded yet (see `demo/README.md`).*

## The three problems it maps to

| Problem | Tool | Who does the work |
|---|---|---|
| Lab data screening: compare every result with the published criteria | `screen_lab_results` | Code only. No language model compares numbers. |
| Guidance search: find the right page in thousands of pages of standards | `search_guidance` | Local hybrid index (keyword plus vector). No language model call. Every passage carries document, page and section. |
| Report drafting: write the results section | `draft_section` | A language model, wrapped by redaction and citation checks. |

A fourth small tool, `list_criteria_sets`, lists the criteria sets that screening accepts. All four tools are read-only.

## How it works

```
Claude Desktop / Claude Code   (host; its chat model is Claude)
        |  MCP over stdio
        v
site-assessment server (Python, FastMCP)
  search_guidance ----> local index (LanceDB: vector + full-text, rank fusion)
  screen_lab_results -> pure Python: lab CSV x criteria table, source page on every row
  draft_section ------> redact client details -> LLM via OpenRouter -> validate citations and numbers -> restore
```

Tool inputs and outputs are in [docs/02-architecture.md](docs/02-architecture.md). Results come back as structured data plus a short text rendering, so hosts that ignore structured output still show something readable. Where the host supports MCP Apps, the exceedance table renders inline.

## Quickstart

Needs [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run python ingest/fetch_sources.py    # downloads the guidance PDFs listed in data/sources.yaml
uv run python ingest/build_index.py      # parses them and builds the local index (CPU only, one-time; tens of minutes on a cold parse, about 6 min when data/cache/docling/ exists)
cp .env.example .env                     # only needed for draft_section; add OPENROUTER_API_KEY
```

Claude Desktop: add this to `claude_desktop_config.json` (replace the path), then restart Claude Desktop.

```json
{
  "mcpServers": {
    "site-assessment": {
      "command": "uv",
      "args": ["--directory", "/path/to/site-assessment-mcp", "run", "site-assess"],
      "env": { "OPENROUTER_API_KEY": "<your key, only needed for draft_section>" }
    }
  }
}
```

Claude Code:

```bash
claude mcp add site-assessment -e OPENROUTER_API_KEY=<your key> -- uv --directory /path/to/site-assessment-mcp run site-assess
```

Streamable HTTP instead of stdio: `uv run site-assess --http --port 8000`. It binds to localhost and has no authentication, so use it locally only.

Try: "Screen the results for site DEMO-03 against the residential criteria", then "What does the guidance say about the exceedances?", then "Draft the results section."

## Design choices

- **Numbers come from code, not the model.** Screening is deterministic Python; the same input gives the same output. The model only writes prose around numbers it was given, and a validator checks every number in the draft against the screening output. See [D6](docs/08-decisions.md).
- **Citations are validated.** The draft must cite `[chunk_id]` for every claim that is not a screening number. Each cited id must be one of the passages supplied to the model, otherwise the sentence is removed and listed in `warnings`. See [D3](docs/08-decisions.md).
- **Redaction before the model provider.** Client names and site addresses are replaced with placeholders before the text leaves the machine, and restored in the returned draft. Redaction covers the OpenRouter hop only; the draft returned to Claude contains the restored names. See [docs/06-guardrails-security.md](docs/06-guardrails-security.md).
- **Synthetic data only.** No real client or site data, ever ([D11](docs/08-decisions.md)).
- **Guidance text is treated as untrusted.** Tool descriptions state that passages are reference text, not instructions, and the drafting prompt delimits them.

Every decision with its alternative and status is in [docs/08-decisions.md](docs/08-decisions.md).

## Evaluation

Tasks are defined in [docs/04-evaluation.md](docs/04-evaluation.md) and live in `evals/` (how to run: [evals/README.md](evals/README.md); per-run rows with token counts and cost are there). Measured on 2026-10-03 with inspect_ai 0.3.275, commit uncommitted (no commits yet), 3 samples (DEMO-01/02/03), temperature 0. Runs A to C used one draw each; the manual-review rerun used 3 draws for drafts and agent cases and was graded by hand, not by a judge model. Failures are published with the passes; cells stay blank until measured.

| Task | Result | Gate or target | Notes |
|---|---|---|---|
| `screening_exact` | 13 / 13 cases exact (accuracy 1.000) | Gate: 100% | Expected outputs hand-computed from the criteria tables, independently of `screening.py`. Covers below LOR, unit conversion, exactly equal, half-up rounding, depth-band boundaries, NL criteria, aliases, duplicates. |
| `pii_leak` | Offline echo model: no_leak 1.0, round_trip 1.0. Real mode, `deepseek/deepseek-v4.1-flash`: no_leak 1.0, redacted_something 1.0. Real mode, `stealth/space-bunny-alpha`: no_leak 1.0, redacted_something 1.0 | Gate: 0 leaks | Negative control: with redaction disabled the offline task scores 0.000, so the check can fail. A grep of all eval logs for the key prefix found nothing. Provider boundary only (see [docs/06](docs/06-guardrails-security.md)). |
| `retrieval_citation` | recall@5 0.85, MRR 0.80 (hybrid) | Target: recall@5 >= 0.8 | 20 questions over 3 documents, index rebuilt after the chunking and ranking fixes (1712 chunks). Golden set is agent-drafted, pending owner review. |
| `draft_faithfulness` | Citation validity 1.0 raw and 1.0 after the validator; number_fidelity 1.0; claim_support 0.933; facts_support 0.825 | Citation validity 100% after validator | Final run C, drafter `stealth/space-bunny-alpha`, judge `google/gemini-3.5-flash-lite`. Runs A and B, and the 7 remaining unsupported verdicts, are in [evals/README.md](evals/README.md). With a flash-lite judge, read facts_support as noisy and conservative. Manual rerun, 9 draws, no judge: cited sentences supported 54 / 56, uncited sentences supported by FACTS 124 / 127. |
| `agent_tool_use` | Run 2: right tools and arguments 36 / 36; manual grade 18 PASS, 16 PARTIAL, 2 FAIL; a09 on the final code 3 / 3 PASS (run 2 predates fixes 3 and 4, which only a09 exercises) | Reported | New: `stealth/space-bunny-alpha` acts as the MCP host over real stdio, 12 cases x 3 draws, cases and rubrics written before any output. PARTIALs are the model adding facts after correct tool calls. Every case graded by hand: [evals/manual_review_2026-10-03.md](evals/manual_review_2026-10-03.md), which also lists the server fixes it led to. |

Retrieval ablation, same 20 questions, before and after the chunking and ranking fixes (recall@5 / MRR):

| Mode | Before | After | recall@5, table lookups | recall@5, narrative (after) |
|---|---|---|---|---|
| bm25 | 0.90 / 0.67 | 0.90 / 0.72 | 0.75 | 1.00 |
| vector | 0.85 / 0.69 | 0.85 / 0.75 | 0.75 | 0.92 |
| hybrid (default) | 0.85 / 0.76 | 0.85 / 0.80 | 0.75 | 0.92 |

What changed: the table caption is repeated in the text of every piece of a split table; separator-only chunks are dropped; the "Notes:" pseudo-heading is removed; each chunk has a `page_end`, and a hit counts when the gold page falls in `[page, page_end]`; and each retrieval leg returns a fixed pool of 30 candidates before rank fusion. The page-span rule adds exactly one hit (r06 in bm25); under the old first-page-only rule recall@5 is 0.85 in all three modes. 183 of 1712 chunks span past their first page (maximum 3 extra pages).

Reading it honestly: the ranking fixes raised MRR in every mode, recall@5 did not move except bm25's page-span hit. BM25 alone still finds the gold page in the top 5 slightly more often; hybrid ranks it higher when found. Table-lookup questions are the weak spot for every mode (0.75). The remaining hybrid misses are r02, r06 and r11, all ranking or wording problems, not missing text. A local cross-encoder reranker is the untested next step.

OCR was assessed and is not needed: the only low-text pages are figures and one blank page in `nepm-asc-b2` (pp.138, 140-144, 150), no golden question targets them, and docling lost no table text (checked against the pypdf text layer). No vision model was used.

Drafting: the first run scored claim_support 0.532 because 17 of the 23 unsupported sentences were statements from the screening FACTS carrying a guidance citation (prompt rule 2 forced a citation on every non-number statement). The prompt was rewritten so FACTS statements are uncited and guidance statements are cited, and a second scorer, `facts_support`, now checks uncited sentences against the FACTS block.

## Models

The chat model in Claude Desktop or Claude Code is Claude. Separately, `draft_section` calls a model server-side through OpenRouter. The default is `deepseek/deepseek-v4.1-flash` (price moves: $0.30 / $1.20 per Mtok on 2026-10-02, $0.02 / $0.42 early on 2026-10-03, back to $0.30 / $1.20 later that day; check the catalog); set `SITE_ASSESS_MODEL` to change it, for example to `anthropic/claude-sonnet-5.5`. The owner runs local evals on the free `stealth/space-bunny-alpha` ($0 / $0), which the OpenRouter catalog lists as expiring 2026-10-05; after that date `SITE_ASSESS_MODEL` must go back to DeepSeek. Stealth models may log prompts; the demo data is fictional and redacted, and the guidance documents are public. No Claude Sonnet comparison has been run (cheap or free models only). Only `draft_section` (and the LLM-graded evals) use this model. `search_guidance` and `screen_lab_results` make no model call.

## Data and licences

- Guidance PDFs are fetched at install time from the publishers listed in `data/sources.yaml`; they are not committed. The WA DWER guideline is not openly licensed and is not redistributable. The licence on the NEPM copies on legislation.gov.au is unverified.
- Criteria values are transcribed by hand from the fetched sources, each with document, page and table recorded, and checked by tests. No value is taken from memory or from a model.
- Lab data and sites are synthetic and labelled as such.
- Details: [docs/03-data.md](docs/03-data.md). Licence for this repo's code: to be set by the owner.

## Limitations

- **Not a compliance tool.** Output is a draft for a qualified person to check. Nothing here is a finding, an opinion or advice.
- One section type (results and discussion), soil criteria only, a short analyte list, three synthetic sites.
- Retrieval and drafting quality are measured only by the evals above: 3 samples, one to three draws, an agent-drafted golden set, and graders from the same model family that built the system (see the manual review).
- Redaction misses unusual name and address forms; see the known limits in [docs/06-guardrails-security.md](docs/06-guardrails-security.md).
- Whatever a tool returns is read by Claude, so what you type and what the tools return go to Anthropic via the host.
- Real client data would need an OpenRouter provider under a data agreement and a deployment review. This demo does not solve that.
- MCP Apps rendering depends on the host. Claude Code does not render it; the text result stands alone.

## Security notes

Threat model, redaction design and the release checklist are in [docs/06-guardrails-security.md](docs/06-guardrails-security.md). The server exposes only its own four read-only tools. Agent Scan result: pending.
