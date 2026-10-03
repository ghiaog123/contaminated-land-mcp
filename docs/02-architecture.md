# Architecture

Status: draft, 2026-10-02. This file is the contract the build lanes code against. Change it first, then the code.

## Components

```
Claude Desktop / Claude Code   (host; its chat model is always Claude)
        |  MCP (stdio; streamable HTTP optional)
        v
contaminated-land MCP server (Python, FastMCP)
  ├── search_guidance ──> retrieval: LanceDB hybrid (vector + full-text, RRF)
  ├── screen_lab_results ──> screening: pure Python over CSV + criteria table
  └── draft_section ──> redact (Presidio) ──> OpenRouter LLM ──> citation validator ──> restore placeholders
                                                    |
offline: ingest pipeline (docling parse ──> chunk ──> embed ──> LanceDB)
offline: eval suite (inspect_ai) ──> results published in README
tracing: OpenInference ──> Phoenix (local)
```

## Directory layout

```
contaminated-land-mcp/
  README.md
  pyproject.toml            # uv project; uv.lock committed
  .env.example              # variable names only, never values
  docs/                     # this folder
  src/contaminated_land/
    server.py               # FastMCP app, tool registration only
    retrieval.py            # search over LanceDB
    screening.py            # CSV + criteria -> exceedances; no LLM
    drafting.py             # prompt, LLM call, citation validation
    redact.py               # Presidio wrapper, reversible placeholder map
    llm.py                  # one OpenRouter client; model id from env
    apps/                   # MCP App HTML for the exceedance table
  ingest/
    fetch_sources.py        # download PDFs listed in data/sources.yaml
    build_index.py          # docling -> chunks -> LanceDB
  data/
    sources.yaml            # every source document: id, title, URL, licence, retrieved date
    criteria/               # assessment criteria tables, each row cites doc + page
    lab/                    # synthetic lab CSVs + site metadata
    cache/                  # parsed docling JSON + index (gitignored or released as an asset)
  evals/                    # inspect_ai tasks + golden sets
  tests/                    # unit tests for screening, redaction, citation validation
  demo/                     # vhs .tape file and the rendered GIF
```

## Tool contracts

All tools return structured output (`structuredContent` with a declared output schema) plus a short text rendering for hosts that ignore structured output. The Python contract is `src/contaminated_land/types.py`; `chunk_id` format is `<doc_id>:p<page>:<nnnn>`, for example `nepm-asc-b1:p12:0003`.

### `search_guidance`

Input:

| Field | Type | Notes |
|---|---|---|
| `query` | string, required | Natural language or exact terms (analyte names, criterion codes). |
| `top_k` | int, default 5, max 20 | |
| `doc_ids` | list[string], optional | Restrict to these source ids from `data/sources.yaml`. |

Output: `{ "results": [Passage] }`, where

```
Passage = {
  "chunk_id": string,      # stable id, used by citations
  "doc_id": string,        # key in data/sources.yaml
  "doc_title": string,
  "page": int,             # 1-based page in the source PDF
  "section": string|null,  # heading path from docling
  "text": string,          # chunk text; tables rendered as markdown
  "score": float
}
```

No LLM call. Passage text is untrusted data (see [06-guardrails-security.md](06-guardrails-security.md)).

### `screen_lab_results`

Input:

| Field | Type | Notes |
|---|---|---|
| `site_id` | string, required | Must exist in `data/lab/sites.yaml`. |
| `criteria_set` | string, required | Id of a table in `data/criteria/`, for example a land-use scenario. Allowed ids are listed by the tool description. |

Output:

```
{
  "site_id": string,
  "criteria_set": string,
  "samples_screened": int,
  "analytes_screened": int,
  "exceedances": [{
    "sample_id": string, "depth_m": float|null, "analyte": string,
    "result": float, "unit": string,
    "criterion": float, "criterion_unit": string,
    "ratio": float,                       # result / criterion, rounded to 2 dp
    "source": {"doc_id": string, "page": int, "table": string}
  }],
  "not_screened": [{"sample_id": string, "analyte": string,
                   "reason": "below_lor"|"no_criterion"|"unit_mismatch"|"no_depth"|"non_numeric_criterion"}],
  "notes": [string],                    # fixed caveats, e.g. duplicates screened separately
  "_meta": {"ui": {"resourceUri": "ui://contaminated-land-mcp/exceedances"}}   # MCP App, optional
}
```

Rules:
- Unit conversion is explicit and tested. An analyte with a unit the code cannot convert goes to `not_screened`, never silently compared.
- Results reported as below the limit of reporting are not exceedances. Handling is recorded per row.
- Same input, same output, byte for byte.

### `draft_section`

Input:

| Field | Type | Notes |
|---|---|---|
| `site_id` | string, required | |
| `criteria_set` | string, required | |
| `section` | enum, default `results_discussion` | Only one section type in the demo. |

Behaviour, in order:
1. Call `screen_lab_results` and `search_guidance` internally.
2. Redact client names, site addresses and other configured entities with Presidio. Keep the placeholder map in memory on the server only.
3. Call the LLM through OpenRouter with the redacted facts and passages. The prompt requires a `[chunk_id]` citation on every claim that is not a number from the screening output.
4. Validate: every cited `chunk_id` must be one of the passages supplied in step 3, and every number must match the screening output. On failure, retry once with the error list, then return the draft with failing sentences removed and listed in `warnings`.
5. Restore placeholders.

Output:

```
{
  "markdown": string,
  "citations": [{"chunk_id": string, "doc_id": string, "page": int}],
  "warnings": [string],
  "model": string,              # the model id actually used
  "redactions": int             # count only, never the values
}
```

## Configuration

| Variable | Required | Meaning |
|---|---|---|
| `OPENROUTER_API_KEY` | yes, for `draft_section` and evals | Never committed. `.env` is gitignored. |
| `CONTAMINATED_LAND_MODEL` | no | OpenRouter model id for `draft_section`. Default `deepseek/deepseek-v4.1-flash` ([D2](08-decisions.md#d2-llm-access-openrouter-status-decided)). |
| `CONTAMINATED_LAND_JUDGE_MODEL` | no | Model id for LLM-graded evals. |
| `PHOENIX_COLLECTOR_ENDPOINT` | no | Enables tracing when set. |

## Where data goes

| Data | Leaves the machine? | To whom |
|---|---|---|
| Guidance PDFs, index, criteria tables | No | |
| Lab CSV values | Only inside `draft_section`, after redaction | OpenRouter, then the provider of `CONTAMINATED_LAND_MODEL` |
| Client names, site addresses | Not to the OpenRouter provider (replaced by placeholders). Yes to the host model, because `draft_section` restores them in its returned draft. | Anthropic, via the host |
| What the user types in Claude, and every tool result | Yes | Anthropic, because the host chat model is Claude. Outside this server's control. |
| Traces | No | Local Phoenix only |

The last row matters: whatever a tool returns is read by the host model. So `screen_lab_results` and `search_guidance` return no client identifiers. `draft_section` reads them from `data/lab/sites.yaml`, sends only placeholders to OpenRouter, and restores them in the draft it returns to the host. A deployment that must keep identifiers away from the host too would return the draft with placeholders and restore them in a separate local step. That is out of scope for the demo and stated in the README.

## Decisions

See [08-decisions.md](08-decisions.md).
