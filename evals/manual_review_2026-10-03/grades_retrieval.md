# Retrieval grades (manual, reading top-5 hybrid passages)

Totals: ANSWERED 17, PARTIAL 1, NOT ANSWERED 2. Auto metric: 17 hit / 3 miss.

| qid | kind | auto | verdict | evidence rank | flags | reason |
|---|---|---|---|---|---|---|
| r01 | table | hit@1 | ANSWERED | 1 | c (minor) | "Table 1A(1) Health investigation levels for soil contaminants" caption + HIL A-D headers repeated per chunk. Footnote digits glued to names ("Arsenic 2", "BaP TEQ 6"); "(mg/kg)" sits inside the Recreational header. Middle metals rows (Cu, Pb, Hg, Ni) not in top 5, not needed for "which table". |
| r02 | table | MISS | NOT ANSWERED | none | pointer only | No top-5 chunk names Table 1A(3) or gives HSL values by soil/depth. Rank 1/2/5 (DWER) only say B1 s.2.4 / "Schedule B1 has the HSLs". |
| r03 | table | hit@4 | PARTIAL | 2 (DWER), 4 (gold) | b | Gold chunk rank 4 is p64 footnotes only (no table, no caption). Rank 2 DWER Table 4 says "Groundwater HSLs for vapour intrusion | ASC NEPM B1 s. 2.4": right concept, but "Table 1A(4)" is never named. Auto-hit overstates. |
| r04 | table | hit@1 | ANSWERED | 1-2 | none | "Table 1A(2) Interim soil vapour health investigation levels..." TCE, PCE, VC rows with headers; VC split into its own chunk with headers repeated (good). |
| r05 | table | hit@2 | ANSWERED | 2, 4 | none | "Table 1B(6) ESLs for TPH fractions F1 - F4, BTEX and benzo(a)pyrene in soil", rows with soil texture and land use. |
| r06 | table | MISS (rank 8) | ANSWERED (weak) | 5 | a | Rank 5 (b1 p26): "The values are included in Table 1B(7) at the end of this Schedule". Names the table, but no values or texture/land-use split. Gold p73 would be the full answer. Possible golden-set issue: gold page too narrow for a "which table" question. |
| r07 | table | hit@1 | ANSWERED | 1 | none | "Table 4. Minimum number of samples recommended for initial assessment of stockpiles", full table, <75 m3 = 3 ... up to 200 m3. |
| r08 | table | hit@1 | ANSWERED | 1 | none | "Table 2: Human health assessment levels for soil" full table. Rank 2/3 are Tables 4/3 (adjacent, correctly titled). |
| r09 | narrative | hit@1 | ANSWERED | 1 | none | "It is not necessary to delineate any contamination at the PSI stage. Limited sampling may be included". Chunk spans p14-15. |
| r10 | narrative | hit@1 | ANSWERED | 1 | none | "required when ... contamination is present or is likely to be present and the information available is insufficient". |
| r11 | narrative | MISS (rank 14) | NOT ANSWERED | none | ranking | Rank 2 says "seven-step DQO process" and that step 7 is the SAQP, but the steps are never listed. |
| r12 | narrative | hit@1 | ANSWERED | 1 | none | "blind replicate samples and rinsate blanks ... to determine the precision of the field sampling". Rank 2 is a mangled table (merged cells repeated). |
| r13 | narrative | hit@1 | ANSWERED | 1 | none | "samples at 0-100 mm or 0-150 mm should be taken". |
| r14 | narrative | hit@1 | ANSWERED | 1 | none | "kept as short as possible"; "screens should not be installed across different geological units"; ~1 m once contamination is suspected. |
| r15 | narrative | hit@1 | ANSWERED | 1 | none | "not clean-up or response levels"; default remediation use may cause unnecessary remediation. |
| r16 | narrative | hit@1 | ANSWERED | 1 | none | "The selected value of 0.005 ... median of the US EPA 2008 attenuation factor database". Chunk spans p15-16. |
| r17 | narrative | hit@1 | ANSWERED | 1 | none | "inappropriate response to declare a site a human health risk on the basis of the presence of bonded ACM alone". |
| r18 | narrative | hit@1 | ANSWERED | 1 | none | "show at least ... sample locations and depths against the laboratory results. Results exceeding investigation threshold levels should be highlighted". |
| r19 | narrative | hit@1 | ANSWERED | 1 | noise | Rank 1 lists regulatory, planning and voluntary triggers. Ranks 2-5 are junk (guideline list, reference lists, glossary). |
| r20 | narrative | hit@1 | ANSWERED | 1 | none | r.31 conditions quoted: certificate of contamination audit request; "every report ... relevant to the investigation, assessment ... of a source site". Rank 5 is an empty report template. |

## Misses

**r02 (soil HSLs for vapour intrusion, Table 1A(3)): ranking/wording, gold is sound.**
- Gold p60 is the real table (PDF p60 = printed p52). Columns are HSL A&B / C / D by depth bands, rows are SAND / SILT / CLAY by chemical.
- Docling stores the title "Table 1A(3) Soil HSLs for vapour intrusion (mg/kg)" as a separate caption item. Gold chunks are mostly NL/number cells.
- The query says "petroleum hydrocarbon vapour intrusion ... soil texture and depth to source". The table text says "Soil HSLs for vapour intrusion" and "SAND/SILT/CLAY" and "0 m to <1 m".
- BM25 found nothing in the top 20. Vector reached rank 16. TOC and DWER narrative about HSLs win.
- I could not see the chunk text for p60. Whether the caption sits in the first chunk is inferred (the r01 chunks do carry the caption).
- p61 carries a known context loss: the chunk starts at "Naphthalene 4 NL ... 10" with no SILT label. The docling table for p61 begins at Naphthalene, so SILT is missing. A reader would think "4" is a sand value.

**r06 (Table 1B(7) management limits): ranking, partly gold-too-narrow.**
- Gold p73 has the full table: F1 700/800, F3 2500/3500 coarse/fine, residential vs commercial.
- Hybrid rank 8; bm25 rank 3, vector none. Narrative chunks (p17 fractions, p24 ESL intro) outrank it.
- The table chunk has no words like "texture", "land use" beyond headers. Its caption "Management Limits for TPH fractions" should match, so the failure is probably vector dilution.
- b1 p26 chunk at rank 5 does answer "which table", so I graded ANSWERED (weak).

**r11 (DQO steps): ranking; gold is good.**
- Gold p125 (b2 App. B, 18.1) lists Steps 1-7 by name.
- p29-30 chunks (ranks 1-2) match the query terms strongly but only describe the process. They say "seven-step" and "SAQP developed in the seventh step", not the names.
- bm25 rank 3; vector none. Hybrid rank 14: p125's chunk has the heading "Appendix B: Data quality objectives (DQO) process" and a short list, likely merged with other text. The list chunk is evidently ranked below the TOC (rank 4) and a reference list (rank 3).
- Not a questionable gold. A "list the steps" query should favour the enumerated list.

## Patterns and chunking issues
1. **Noise chunks take top-5 slots.** TOC (b1 p6, b2 p7, b1 p7), reference lists (b1 p84, b2 p118, p119), glossary (dwer p101), empty report templates (dwer p112, p129). They appear in r02, r03, r05, r06, r08, r11, r16, r19, r20. Score is above 0.029 in many cases, so they beat real content. Suggest dropping TOC/references/glossary at index time or down-weighting them.
2. **Table fragments are tiny but headers are repeated.** Docling splits a table into 1-5 row chunks, each repeated with header (good: r01, r04, r05). But the table caption appears only on the first fragment (r01 0152/0153, r05 0207 have no caption), so later fragments rely on header text alone. Fragments like r04 0165 (1 row) retrieve poorly alone.
3. **Soil-type/section labels in-row, not in header.** Tables 1A(3)/1A(4) use SAND/SILT/CLAY as row-group labels. On a continuation page the label is lost (p61 naphthalene "4"; p64 "F1 (7) 6 6 6" begins before CLAY). This is a correctness risk even when the page is retrieved. Fix: carry the current row-group label into every chunk.
4. **Numeric-only tables embed badly.** NL/number cells give no lexical or semantic hook. Both big HSL tables (1A(3), 1A(4)) failed or were weak (r02 miss, r03 gold chunk was notes only).
5. **Footnote digits glued to names** ("Arsenic 2", "PCBs 8", "BaP TEQ 6") and units inside header cells. Minor, but a reader can mistake the footnote for part of the value or name.
6. **Merged-cell tables flatten badly** (b2 p132 rows repeat "Precision quantitative measure..." three times; b2 p86 ACM table; dwer p101 glossary lost its table structure). Chunk text stays readable only by luck.
7. **Notes separated from the table they qualify**, e.g. p64 footnotes (r03, r16 rank 5) rank without the table. The p67-68 chunk fuses notes 7-9 with the next table heading ("Table 1B(1)").
8. **Narrative chunking works well:** all 11 narrative questions were answered at rank 1 (r09-r20 except the r11 miss).
9. **Auto-metric agreement:** the metric overstated on r03 (hit, graded PARTIAL) and understated on r06 (miss, graded ANSWERED weak). Net: 17 ANSWERED vs 17 auto hits, but not the same set.
