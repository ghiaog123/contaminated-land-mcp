# Data: sources, criteria, synthetic lab data, cache

Status: draft, 2026-10-02.

Contracts this file must match: [02-architecture.md](02-architecture.md) (tool contracts, directory layout), [08-decisions.md](08-decisions.md) (D6, D11), [09-build-plan.md](09-build-plan.md) (lanes A and B). Evaluation of this data: [04-evaluation.md](04-evaluation.md).

Hard rule (D11): this file contains no criterion values. Every criterion number enters the repo only by transcription from a fetched primary source, with doc, page and table recorded, and is checked by a test (section 2).

## 1. Source documents

Candidate list, checked 2026-10-02. "Verified" means URL fetched and publisher and document identity confirmed. Licence is verified only where a licence statement was actually read.

| doc_id | title | publisher | URL | licence | verified? | why included |
|---|---|---|---|---|---|---|
| `nepm-asc-b1` | NEPM ASC, Schedule B1 "Guideline on Investigation Levels for Soil and Groundwater" (2013 amended compilation, 89 pp as served) | National Environment Protection Council; administered by the Department of Climate Change, Energy, the Environment and Water | https://www.legislation.gov.au/F2008B00713/2013-05-16/2013-05-16/text/original/pdf/2 | Unverified. No licence statement found on the document or the Details page (https://www.legislation.gov.au/Details/F2013C00288). Check the Federal Register copyright page at build time. | URL: yes (HTTP 200, PDF, title "Schedule B1"). Licence: no. | Source of HIL, HSL, EIL/ESL and management-limit tables. Core criteria source for `screen_lab_results`. |
| `nepm-asc-b2` | NEPM ASC, Schedule B2 "Guideline on Site Characterisation" (2013 amended compilation, 150 pp as served) | as above | https://www.legislation.gov.au/F2008B00713/2013-05-16/2013-05-16/text/original/pdf/3 | Unverified, as above. | URL: yes (HTTP 200, PDF, title "Schedule B2"). Licence: no. | Sampling, QA/QC and reporting guidance. Gives `search_guidance` and `draft_section` real narrative to cite. |
| `nepm-asc-measure` | NEPM ASC, Measure text (Volume 1 of the 22-volume compilation F2013C00288, 21 pp as served) | as above | https://www.legislation.gov.au/F2008B00713/2013-05-16/2013-05-16/text/original/pdf/1 | Unverified, as above. | URL: yes (HTTP 200, PDF). Licence: no. | Optional. Legal framing and definitions. Drop if retrieval eval shows it adds noise. |
| `dwer-acs-2021` | Guideline: Assessment and management of contaminated sites (Nov 2021, last updated 16 Jun 2023, 178 pp as served) | Department of Water and Environmental Regulation (WA) | https://www.wa.gov.au/system/files/2023-05/guideline-assessment-and-management-of-contaminated-sites.pdf (landing page: https://www.wa.gov.au/government/publications/guideline-assessment-and-management-of-contaminated-sites) | Not open. The PDF states "all other rights are reserved" and permits reproduction in unaltered form only, for personal non-commercial or in-organisation use. | URL: yes. Licence: yes (read in the PDF front matter). | State layer on top of the NEPM. Shows how a regulator frames assessment and reporting. |

Notes:
- The nepc.gov.au pages for Schedule B1 (for example https://www.nepc.gov.au/sites/default/files/2022-09/schedule-b1-guideline-investigation-levels-soil-and-groundwater-sep10.pdf) appeared in search results but did not respond to fetch from this environment, so they are unverified. The legislation.gov.au copy is the registered 2013 compilation and is preferred as `url`. The nepc.gov.au file name suggests a September 2010 version (unverified); do not use it for criteria unless its content is shown to match the 2013 compilation.
- The legislation.gov.au URLs above use a document-series path (`F2008B00713`) with the page numbers 1, 2, 3 observed to map to the Measure text, Schedule B1 and Schedule B2. This mapping was observed on 2026-10-02 and could change. Re-check at build time.
- Table identifiers seen in the Schedule B1 text: Table 1A(1) (HIL), 1A(3) (soil HSL for vapour intrusion), 1A(4) (groundwater HSL), 1B(4), 1B(5), 1B(6), 1B(7). The exact criteria_set mapping is decided from the fetched text, not from this list.
- A current-version check is needed: the NEPM may have been varied since the 2013 compilation. Unverified.
- Maximum of four documents. Do not add documents without a stated criteria or eval need.

### `data/sources.yaml` schema

```yaml
- id: nepm-asc-b1            # stable key; used as doc_id everywhere
  title: "..."               # as printed on the document
  publisher: "..."
  url: "https://..."         # direct PDF URL
  landing_url: "https://..." # optional human page
  licence: "..."             # verbatim licence statement or "unverified"
  licence_checked: 2026-10-02
  redistributable: false     # true only if the licence allows committing the PDF
  retrieved: 2026-10-02      # date fetch_sources.py downloaded it
  sha256: "..."              # of the downloaded bytes; build fails if it changes silently
  pages: 0                   # recorded at fetch time
```

`sha256`, `retrieved` and `pages` are written by `ingest/fetch_sources.py`, not by hand. A changed hash means a changed source: re-run the criteria transcription check before accepting it.

## 2. Criteria tables (`data/criteria/`)

One CSV per `criteria_set`. A criteria_set is one table-and-scenario slice of a source document, so that the id the user passes to `screen_lab_results` selects exactly one column or matrix of published values.

Proposed ids (final list is set when the tables are read; ids are lowercase kebab):

| criteria_set | Slice | Source table (to confirm) | Matrix |
|---|---|---|---|
| `hil-a-residential` | Health investigation levels, residential with garden/accessible soil | `nepm-asc-b1` Table 1A(1) | soil |
| `hil-b-residential-minimal` | HIL, residential with minimal soil access | `nepm-asc-b1` Table 1A(1) | soil |
| `hil-c-public-open-space` | HIL, public open space | `nepm-asc-b1` Table 1A(1) | soil |
| `hil-d-commercial` | HIL, commercial/industrial | `nepm-asc-b1` Table 1A(1) | soil |
| `hsl-a-b-vapour-intrusion` | HSL for vapour intrusion, residential, by soil type and depth band | `nepm-asc-b1` Table 1A(3) | soil |
| `hsl-d-vapour-intrusion` | HSL for vapour intrusion, commercial/industrial, by soil type and depth band | `nepm-asc-b1` Table 1A(3) | soil |

Scope limit for the demo: soil only, a short analyte list sufficient for the three demo sites (some metals, some petroleum hydrocarbon fractions and BTEX). Groundwater, soil vapour, EIL/ESL and management limits are out of scope until needed. The analyte list is chosen from what the tables contain.

### Row schema

| Column | Type | Notes |
|---|---|---|
| `analyte` | string | Canonical name used by the matcher. |
| `cas_no` | string | CAS number where the source gives one or the analyte is a single substance; empty for fractions and groups. |
| `criterion` | number | Transcribed value. Never computed, never converted at rest. |
| `unit` | string | Unit exactly as the source table states. |
| `matrix` | enum | `soil` in the demo. |
| `land_use` | string | Source scenario label, for example the HIL letter. |
| `soil_type` | string | Required for HSL (source soil classes), empty for HIL. |
| `depth_band` | string | Required for HSL (source depth intervals), empty for HIL. |
| `source_doc_id` | string | Key in `data/sources.yaml`. |
| `page` | int | 1-based page in the PDF as served, same convention as `Passage.page` in [02-architecture.md](02-architecture.md). |
| `table_ref` | string | Table identifier as printed, for example "Table 1A(1)". Feeds `source.table` in the tool output. |
| `notes` | string | Footnote numbers or qualifiers from the source that affect use (for example "not limiting"). |

Rules:
- A row without `source_doc_id`, `page` and `table_ref` is invalid. Loading fails.
- Source cells that are not numbers (for example "not limiting", "see note") are kept as rows with an empty `criterion` and the text in `notes`. Screening routes them to `not_screened`, never to a comparison.
- The criteria_set must match the site: `sites.yaml` carries `land_use` and `soil_type`, and the screening code rejects a set whose scenario contradicts them with an explicit error instead of silently screening.

### Transcription check (`tests/test_criteria_transcription.py`)

For every row:
1. Open the PDF cached by `fetch_sources.py` (verifying its `sha256`), extract the text of the cited `page` with a parser independent of docling (for example pdftotext or pypdf).
2. Assert the page text contains `table_ref`.
3. Assert the page text contains the formatted `criterion` as printed in the source (match on the source string, normalising thousands separators and whitespace, not on float equality).
4. Assert the page text contains the analyte name (or a recorded alias) near the value on the same row, using a line-level match. Rows the extractor cannot lay out line-by-line are listed in a small explicit allowlist with a reason, and a human checks them.

Limits, stated plainly: this proves the number appears on the cited page, not that it is in the right row or column. A second human pass spot-checks a sample of rows per criteria_set against the rendered PDF, and the sample is recorded in the PR. Table layout in PDFs can defeat line matching; those rows are the allowlist.

## 3. Synthetic lab data (`data/lab/`)

Every file starts with a header comment: `# SYNTHETIC DATA. Generated by data/lab/generate.py with seed N. Not real. Client names and addresses are fictional.` The generator is seeded, committed, and idempotent: same seed, same bytes. Files are committed so tests and evals do not depend on running the generator.

### `sites.yaml`

```yaml
- site_id: DEMO-01
  client_name: "..."       # obviously fictional; used to test redaction
  site_address: "..."      # obviously fictional
  land_use: residential-a  # scenario label; must correspond to a criteria_set family
  soil_type: sand          # source soil class; used for HSL
  story: "..."             # one-line intent, for humans and eval authors
```

Client names and addresses must be clearly fake (for example "Example Holdings Pty Ltd", a street that does not exist) and contain at least one multi-token name and one full street address so Presidio has something realistic to catch. They must not be real organisations or places.

### Results CSV (`data/lab/<site_id>.csv`)

| Column | Notes |
|---|---|
| `site_id` | Must exist in `sites.yaml`. |
| `sample_id` | Per site; duplicates are separate sample ids that reference a parent in `lab_ref`. |
| `sampled_date` | ISO date. |
| `depth_m` | Float; may be empty (maps to `depth_m: null` in the tool output). |
| `matrix` | `soil` in the demo. |
| `analyte` | As a lab would print it, including awkward aliases. |
| `cas_no` | May be empty. |
| `result` | Number as reported. For a non-detect, the value is the LOR and `qualifier` is `<`. |
| `unit` | Lab unit, for example mg/kg or ug/kg. |
| `qualifier` | Empty, or `<` for below the limit of reporting. |
| `lor` | Limit of reporting, same unit as `result`. |
| `lab_ref` | Synthetic certificate id; for duplicates, also names the parent sample. |

### Screening semantics (the contract the edge cases test)

- **Exceedance means `result` strictly greater than `criterion`**, after unit conversion into the criterion's unit. A result exactly equal to the criterion is not an exceedance.
- A row with `qualifier = <` is never an exceedance and is recorded in `not_screened` with a below-LOR reason. This follows the rule in [02-architecture.md](02-architecture.md#screen_lab_results).
- Unit conversion is limited to a small explicit table (mass-fraction units of the same dimension, for example mg/kg to ug/kg). Any other unit goes to `not_screened`.
- An analyte with no criterion in the chosen criteria_set goes to `not_screened`.
- Duplicates are screened as separate samples. The demo does not average or pick the worst. This is stated in the tool output so a reviewer is not misled. Handling of duplicates under QA/QC guidance is described in the source documents and is not implemented.

### Designed edge cases

Each case is built by the generator with a fixed id so tests can assert on it. Numeric values are generated relative to the loaded criterion at generation time (for example "criterion exactly", "criterion plus one reporting increment"), never typed into this document.

| Case | Construction | Expected outcome |
|---|---|---|
| Below LOR | `qualifier = <`, `result` equals `lor`, LOR possibly above the criterion | `not_screened`, reason below LOR; not an exceedance even if LOR > criterion |
| Unit conversion | Same analyte reported in ug/kg while the criterion is in mg/kg | Converted, then compared; output reports the criterion unit |
| Unknown analyte | An analyte name absent from the criteria_set | `not_screened`, reason no criterion |
| Unconvertible unit | A unit outside the conversion table (for example a concentration unit of a different dimension) | `not_screened`, reason unit mismatch; never compared |
| Exactly equal | `result` constructed equal to the criterion after conversion | Not an exceedance |
| Just over | `result` constructed one reporting increment above the criterion | Exceedance, `ratio` rounded to 2 dp |
| Duplicate | Two samples with the same location and depth, one parent, one duplicate, different results | Both screened independently |
| Depth bands | Samples either side of a depth-band boundary used by the HSL table | Each matched to the correct band; a sample with no depth goes to `not_screened` for depth-dependent criteria |
| Alias | Lab spelling differing from the canonical analyte name | Matched via alias table, or `not_screened` if no alias is recorded |

### Demo sites

| site_id | Intended story | Primary criteria_set | Edge cases carried |
|---|---|---|---|
| DEMO-01 | Clean residential lot. Zero exceedances. Shows that "no exceedance" is a valid, reported outcome and that below-LOR rows are listed, not hidden. | `hil-a-residential` | below LOR, unknown analyte, one exactly-equal row |
| DEMO-02 | Former fuel storage. One petroleum hydrocarbon hotspot in a shallow sample, declining with depth. Drives the vapour-intrusion HSL, soil type and depth-band matching. | `hsl-a-b-vapour-intrusion` | depth bands, unit conversion, duplicate, just over |
| DEMO-03 | Fill material with a few metals above HIL. Multiple analytes, one sample with several exceedances. | `hil-a-residential` (a second run on `hil-d-commercial` shows the criteria_set changing the result) | alias, unconvertible unit, just over |

Whether the hydrocarbon story needs a second criteria_set (for example a management-limit table) is open and is decided when the tables are read.

## 4. Ingest cache policy

| Path | Contents | Committed? | Rebuilt by |
|---|---|---|---|
| `data/cache/pdf/` | Downloaded source PDFs | No (gitignored) | `ingest/fetch_sources.py` from `data/sources.yaml` |
| `data/cache/docling/` | Parsed docling JSON, one per `doc_id` | No (gitignored) | `ingest/build_index.py` |
| `data/cache/lancedb/` | LanceDB table: chunks, embeddings, full-text index | No (gitignored) | `ingest/build_index.py` |

Policy:
- Everything under `data/cache/` is derived and rebuildable. Nothing in it is edited by hand.
- PDFs are not committed. `redistributable` in `data/sources.yaml` defaults to false and is set true only after the licence has been read and allows redistribution. As of 2026-10-02 the DWER guideline is not redistributable (unaltered personal or in-organisation use only), and the licence of the legislation.gov.au NEPM documents is unverified, so none are committed.
- The parsed docling JSON and index are derived works of those PDFs. Do not publish them as a release asset unless the licence for each source allows it. Default: users build locally. The first build downloads docling models (D4) and takes minutes.
- `fetch_sources.py` records `sha256`, `retrieved` and `pages` per document and fails loudly on a hash change.
- The README quotes short passages only through the tool output (with page citations), not by bundling the documents.
- Criteria values in `data/criteria/` are facts transcribed with attribution (doc, page, table). Whether that is acceptable redistribution under each licence is a licence question, not settled here. Unverified; resolve before the repo goes public.

## Open items

| Item | Needed for |
|---|---|
| Licence of the legislation.gov.au NEPM compilation (Federal Register copyright terms) and of nepc.gov.au copies | Whether criteria CSVs and any quoted text can be published |
| Whether the 2013 compilation is the current in-force version of Schedule B1 | Correctness of criteria |
| Final criteria_set list and analyte list | After reading the tables |
| DWER guideline: does it add anything beyond narrative? | Keep or drop `dwer-acs-2021` |
