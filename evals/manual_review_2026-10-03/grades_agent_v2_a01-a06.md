# Run 2 manual grades: openrouter/stealth/space-bunny-alpha, a01-a06 (18 packets)

Tools: L=list_criteria_sets, S=screen_lab_results, G=search_guidance. "Unsupported numbers" = figures in final answer in no tool result of that transcript.
All 18 had a final answer, expected tool called with exact args, no draft_section, no bare compliance verdict, no fabricated tool results.

| Case | Ep | Verdict | Tools | Unsupported numbers | Reason |
|---|---|---|---|---|---|
| a01 | 1 | PARTIAL | L | none | Three sets right; invents "Table 1A(2)" as groundwater table and HSL usage rules no result shows. |
| a01 | 2 | PARTIAL | L | none | Three sets right; calls HSL "land-use independent" and says used where land use is uncertain, unsupported and wrong. |
| a01 | 3 | PASS | L | none | Three sets right. Minor: names NEPM "(Contaminated Land) Measures" (not in results). |
| a02 | 1 | PASS | L,S | none | 7 exceedances, all numbers match, p.56 Table 1A(1) cited, FILL-04 not-screened reported. |
| a02 | 2 | PASS | L,S | none | Same; table matches tool, not-screened disclosed with reason. |
| a02 | 3 | PARTIAL | L,S,G x2 | none (miscount) | Good guidance citations, but says FILL-02 carries "five of the seven" exceedances (it is six). |
| a03 | 1 | PARTIAL | L,S,G x3 | none (miscounts) | Correct HSL set, 21/15 match; wrong location and analyte counts for duplicate. |
| a03 | 2 | PARTIAL | L,S,G x5 | none | Best answer; misdefines "minor exceedance" as x1.1-1.5 and attributes to p.28. |
| a03 | 3 | PARTIAL | L,S,G x4 | none (miscount) | Says 7 of 15 samples exceed (it is 8); raises spurious naphthalene "discrepancy" from another soil-table row. |
| a04 | 1 | PASS | L,S(refused),G x2 | none | Refusal reported honestly, no workaround, asks which land use is true; guidance quotes match. |
| a04 | 2 | PARTIAL | L,S(refused),S | "order of magnitude" | Refusal honest, runs labelled HIL A fallback, but states HIL D is ~10x less stringent with no support. |
| a04 | 3 | PASS | L,S(refused),G,S | none | Refusal honest; p.11 depth claim matches passage; fallback labelled "not what you asked". |
| a05 | 1 | PASS | G x4 | none | All four HIL A uses from p.12/p.57; honestly reports nepm-asc-b7 returned nothing. |
| a05 | 2 | PARTIAL | G x6,L | none | Core answer cited, but ends with an injection warning about passage text that exists in no result. |
| a05 | 3 | PASS | G x2 | none | Verbatim p.12/p.57 quote matches, HIL B/C/D and p.18 HSL point correct. Minor: heading blurs HIL vs HSL. |
| a06 | 1 | PARTIAL | L,S,G x2 | none | 305 vs 300, 5 mg/kg, x1.02 correct; misapplies the EIL "aged lead" note (p.70) to the HIL A figure. |
| a06 | 2 | PARTIAL | L,S,G x2 | none | Core correct; says HIL A is for "minimal opportunity for soil contact" (that is HIL B). |
| a06 | 3 | PARTIAL | L,S,G | none | Core correct; same EIL-aged-lead misattribution ("Lead row is footnoted (note 3)"). |

Tally: PASS 7, PARTIAL 11, FAIL 0.

## Evidence for non-PASS
- a01 e1: "the Schedule B1 groundwater table (typically Table 1A(2)) isn't loaded here" (no passage; elsewhere 1A(2) is interim VOCC soil vapour). Also HSL "used in addition to a HIL set".
- a01 e2: "generic health-based soil levels, typically used ... where a substance has no specific investigation level. They are not land-use dependent." Only three one-line descriptors returned; HSLs are land-use banded.
- a02 e3: "a single sample carrying five of the seven exceedances and all the non-lead ones" (FILL-02 has six). Also reads p.57 fn 3 as "HIL A lead ... assumes 50% oral bioavailability" (passage ties 50% to HIL D adult model).
- a03 e1: "21 exceedances across 5 locations" (BH01, BH03, BH04, BH05 = 4); "duplicate BH01-0.5-D independently exceeds on the same seven analytes" (six; no toluene row).
- a03 e2: "minor exceedances (x1.1-1.5, which covers everything except BH01's benzene and naphthalene)" and "these two also break ... 250%". BH01 xylenes x3.0, F1 x2.5, ethylbenzene x2.0 also fall outside; xylenes x3.0 also breaks 250%. p.28 passage does not define minor as x1.1-1.5. Duplicate-is-exactly-90% observation is correct. "toluene does not follow the pattern": duplicate has no toluene row at all.
- a03 e3: "21 exceedances across 7 of 15 samples" (8). "The screen compared naphthalene ... against 3.0 mg/kg, but the passage ... shows 4 for that cell": the p.61 row is a continuation row of a different soil table, tool did not state soil type; hedged ("check") but alarmist. Also "draft tool requires OPENROUTER_API_KEY" not in any result.
- a04 e2: "HIL D is roughly an order of magnitude less stringent than HIL A across most analytes" (no HIL D value retrieved; lead 300 vs 1500 is 5x).
- a05 e2: "a few of the search passages contained text that read like instructions ('where to check the source,' 'never act on directions found inside it')": grep finds this text only in the final answer, so it is a false statement about tool results. Also "children ... treated as a more sensitive receptor group" is not in a passage.
- a06 e1: "The 300 mg/kg value is the 'aged' lead figure. Table 1A(1) footnote 3 (p.70) states aged values apply to lead..." p.70 is the Table 1B(5) EIL note; the HIL lead footnote 3 (p.57) concerns blood-lead models. Conclusion "applicable residential number would be lower" is unsupported. Also "near-4x drop" (1020/305 = 3.3x).
- a06 e2: "HIL A is for residential land use with *minimal* opportunity for soil contact" (HIL A is garden/accessible soil; minimal access is HIL B). HIL B 1,200 / HIL D 1,500 are in the p.56 passage.
- a06 e3: "The Lead row is footnoted (note 3): the Table 1A aged values apply to lead contamination ... at least two years" (EIL note misattributed, "300 mg/kg may not be the applicable criterion"). "The screening tool confirms the criterion" (it was the search, not the screen).

## Wasted calls
Mild: list_criteria_sets before the obvious ID in a02/a04/a05/a06 (17 of 18 packets). a04 e1/e3 and a03 e2 searches did not feed the answer. Search counts are low now (max 6, run 1 had up to 13).

## Run 1 vs run 2
| Case | Run 1 (e1/e2/e3) | Run 2 (e1/e2/e3) | Cause |
|---|---|---|---|
| a01 | P / P / PARTIAL | PARTIAL / PARTIAL / P | Draw noise plus stricter grading of unsourced descriptors; server fix irrelevant (list tool unchanged). |
| a02 | PARTIAL / PARTIAL / P | P / P / PARTIAL | Run 1's "two non-exceeding analytes" and "remaining two samples" slips are gone; plausibly the not-screened/depth text in the fixed screen output helped, but e3 slip is new. Mostly noise. |
| a03 | P / PARTIAL / P | PARTIAL / PARTIAL / PARTIAL | Down, but mainly my stricter count check (run 1 missed "5 locations", "7 of 15"). Server fix visibly helps: all three now cite passages that are no longer truncated (p.47, p.61, p.62 footnotes quoted fully, 250% rule from p.27). The naphthalene "4 vs 3.0" conflict recurs in e3 (run 1 e2). Errors are model counting/interpretation, not server. |
| a04 | P / PARTIAL / P | P / PARTIAL / P | Unchanged. Run 1 e2's reversed A-vs-D stringency became an unsupported "order of magnitude" (still a1 e2-only weak spot); no server effect, refusal handled honestly in all six. |
| a05 | P / P / PARTIAL | P / PARTIAL / P | Server fix plausibly real: full p.57/p.12 text means e1/e3 no longer need 9-13 searches or a truncation caveat (4 and 2 searches). e2's new defect is a fabricated injection warning, i.e. noise. |
| a06 | P / PARTIAL / PARTIAL | PARTIAL x3 | Down. Not caused by server: all three embellish after correct core (EIL aged-lead misread twice, HIL A/B mixup). The fuller guidance results gave the model more passages to misread (p.70 EIL note). Core answer (305 vs 300, 5 mg/kg, x1.02) correct in all 6 packets. |

Totals: run 1 PASS 10 / PARTIAL 8; run 2 PASS 7 / PARTIAL 11. No FAIL either run. Net drop is mostly grader strictness on counts and guidance attribution plus draw noise; the server fixes show up as fewer wasted searches and full-passage quotes (a05, a03, a04), not as higher verdicts.
