# Manual grades: DEMO-02 drafts (epochs 1-3)

Legend: S = SUPPORTED, P = PARTIAL (0.5), U = UNSUPPORTED, C = CONTRADICTED. Cited ids: A = nepm-asc-b1:p60:0167 (Table 1A(3) header), B = nepm-asc-b1:p60:0170 (SAND rows), D = nepm-asc-b1:p65:0184 (notes 6-8), E = nepm-asc-b1:p48:0129 (worked-example flowchart steps 1-2).
Common caveat on B: passage 0170 is the SAND row block with no column headers; mapping columns to depth bands relies on 0167 header / table layout. Every B-cited sentence below checks out numerically against that layout (0-<1, 1-<2, 2-<4, 4+ columns).

## Epoch 1 (32 sentences, 12 cited / 20 uncited)
| n | cited | verdict | reason |
|---|---|---|---|
| 1 | - | S | site/client/address/land use/soil in FACTS |
| 2 | - | S | story in FACTS |
| 3 | - | S | criteria_set |
| 4 | A | S | header: Table 1A(3) soil HSLs VI; HSL A&B low-high density residential depth bands |
| 5 | B | S | SAND rows present; "applicable" comes from soil_type=sand + criterion source in FACTS (borderline, passage alone does not say "applicable") |
| 6 | D | S | note 6 sand~coarse; uncertainty: conservative or lab |
| 7-11 | - | S | counts and notes all in FACTS |
| 12 | - | S | mandated screening-not-risk statement (rule 5) |
| 13 | - | S | depth-matched criteria consistent with FACTS note/story |
| 14 | B | S | Toluene, Ethylbenzene, Xylenes, Naphthalene, Benzene, F1, F2 rows exist |
| 15 | - | S | duplicate note |
| 16 | B | S | Benzene/F1/Xylenes rows exist |
| 17 | - | S | BH03 4500 ug/kg vs 3.0 mg/kg, conversion note |
| 18 | B | S | Naphthalene row exists |
| 19 | - | S | xylene criteria 40/60/95 by depth band in FACTS |
| 20 | B | S | Xylenes row exists |
| 21 | - | S | BH04 50 -> 77.5 -> 132.5 increases with depth; story says declines; follows from FACTS (honest flag) |
| 22 | B | S | Benzene row exists |
| 23-26 | - | S | not-screened lead-in and 3 bullets: all 15 pairs present and correctly grouped (non-numeric 6, LOR 8, no_depth 1) |
| 27 | E | S | step 1 question states it (note: passage is a worked example for a different site, presented as "the supplied sequence") |
| 28 | - | S | FACTS contain no groundwater results |
| 29 | E | S | step 2 "Is biodegradation applicable?" with HSL adjustment in same step |
| 30 | E | P | "Further assessment should resolve biodegradation applicability before applying any HSL adjustment": passage only shows the order of steps in a worked example; "should ... before" is an added obligation |
| 31 | D | S | conservative approach or lab analysis |
| 32 | - | S | mandated caveat/screening statement |

Scores: claim_support = 11.5/12 = 0.958; facts_support = 20/20 = 1.000.
Table numbers vs FACTS: all 21 exceedance rows (results, criteria, ratios, units) match; depth bands correct (0.5->0-<1, 1.5->1-<2, 0.99->0-<1, 1.99->1-<2, 3.99->2-<4).

## Epoch 2 (32 sentences, 12 cited / 20 uncited)
| n | cited | verdict | reason |
|---|---|---|---|
| 1-4 | - | S | site details, story, criteria set, 15/7 counts |
| 5 | A | S | header |
| 6 | B | S | same borderline "applicable" as E1 S5 |
| 7 | D | S | note 6 |
| 8-10 | - | S | notes: depth bands, exceedance definition, LOR not compared, duplicates independent |
| 11 | - | S | mandated screening-not-risk statement |
| 12,13,14,16,18,19,20 | B | S | each states the named analyte row exists in SAND block (Benzene, Ethylbenzene, F1, F2, Naphthalene, Toluene, Xylenes); true but content-light |
| 15 | D | S | note 7: F1 = C6-C10 minus BTEX |
| 17 | D | S | note 8: F2 = >C10-C16 minus naphthalene |
| 21 | - | S | criterion source nepm-asc-b1 p60 Table 1A(3) in FACTS |
| 22 | - | S | BH01-0.5: 7 analytes, correct |
| 23 | - | S | BH01-0.5-D: 6 analytes (no Toluene), correct |
| 24 | - | P | "These entries demonstrate that the duplicate results were not averaged": content is in FACTS note, but listing two rows does not "demonstrate" it; framing is invented inference |
| 25 | - | S | BH01-1.5 B/F1/Xyl exceed; Eth/Naph non_numeric_criterion |
| 26 | - | S | 4500.0 ug/kg, 3.0 mg/kg, ratio 1.5 |
| 27 | - | S | BH04 0.99/1.99/3.99 |
| 28 | - | S | follows (BH04 exceedances to 3.99 m) |
| 29 | - | P | "accompanies, rather than changes, the supplied site story": interpretive judgement not in FACTS; glosses over that BH04 xylene rises with depth, against the story |
| 30 | - | S | BH05-0.5 0.6 vs 0.5, 1.2 |
| 31 | - | S | |
| 32 | - | S | LOR note; no_depth not banded follows from reason code |

Scores: claim_support = 12/12 = 1.000; facts_support = 19/20 = 0.950.
Table numbers vs FACTS: all 21 exceedances and all 15 not-screened pairs with correct reason codes; unit shown on result only, criterion column in mg/kg (correct).

## Epoch 3 (22 sentences, 9 cited / 13 uncited)
| n | cited | verdict | reason |
|---|---|---|---|
| 1-4 | - | S | site, story, criteria set, counts |
| 5 | A | S | header |
| 6 | D | S | sand may be applied as coarse (omits AS 1726 qualifier, vague "described in the passage", but accurate) |
| 7-9 | - | S | notes |
| 10 | - | S | note incl. 1.0 m -> 1 m to <2 m |
| 11 | - | S | mandated statement |
| 12 | B | S | benzene 0.5 in all residential bands |
| 13 | B | S | ethylbenzene 55 (0-<1 m) |
| 14 | B | S | F1 45 (0-<1) and 70 (1-<2) |
| 15 | B | S | F2 110 (0-<1) |
| 16 | - | S | BH03 unit note |
| 17 | B | S | naphthalene 3 (0-<1) |
| 18 | B | S | toluene 160 (0-<1) |
| 19 | B | S | xylenes 40 (0-<1: 0.5, 0.99), 60 (1-<2: 1.5, 1.99), 95 (2-<4: 3.99): all correct |
| 20 | - | S | BH01 0.5 m higher than 1.5 m for Benz/F1/Xyl; BH04 to 3.99 m |
| 21 | - | S | non-uniform pattern follows from FACTS; flags tension with story |
| 22 | - | S | lead-in to not-screened table |

Scores: claim_support = 9/9 = 1.000; facts_support = 13/13 = 1.000.
Table numbers vs FACTS: 21 exceedances grouped by analyte (4+2+3+2+3+1+6), all results/criteria/ratios match; 15 not-screened rows match.

## Section-level checks
| check | E1 | E2 | E3 |
|---|---|---|---|
| all exceedances covered | yes (21) | yes (21) | yes (21) |
| all not-screened covered | yes (15, grouped by reason) | yes (15, table) | yes (15, table) |
| numbers not in FACTS | none | none | none (1.0 m, 1 m to <2 m are from FACTS note) |
| compliance/safety verdict | none; states screening-not-risk twice | none | none |
| next-step/recommendation | one weak (S30, PARTIAL); cites worked example as if generic | none | none |
| reviewer-editable | Good: sample-grouped, honest BH04 flag, but 4 sentences on a worked-example flowchart add little and mildly mislead | Fair: 7 near-identical filler bullets, redundant prose repeating tables, two interpretive sentences to cut | Best: analyte-grouped, each cited sentence states band values; short; edit-light |

## Cross-epoch patterns
- No UNSUPPORTED or CONTRADICTED sentences in any epoch; no invented numbers; all exceedances and not-screened pairs complete in all three.
- Weak spots are all PARTIAL and all are inferential framing rather than facts: an unsupported "should" (E1 S30), "demonstrate" (E2 S24), "accompanies rather than changes the story" (E2 S29).
- E1 is the only one that cites the worked-example flowchart (0129) and treats it as general guidance; it is a case-study for another site (soil 2-4 m, groundwater 6 m). E2/E3 avoid it.
- Rule-7 compliance differs in quality: E3's cited sentences carry actual criterion values per band (verifiable); E1/E2 cite "row exists" (true, low information).
- All B-cited sentences rely on band-column layout not explicit in the cited chunk (no headers in 0170); fine here, fragile in general.
- Length: E1 22k, E2 18k, E3 14k output tokens; quality inversely related to length.

## Worst 3 sentences
1. E1 S30 (PARTIAL): "Further assessment should resolve biodegradation applicability before applying any HSL adjustment [nepm-asc-b1:p48:0129]." Passage is a worked example whose answer is YES; it states no obligation or sequencing requirement.
2. E2 S29 (PARTIAL): "This location-specific sequence accompanies, rather than changes, the supplied site story of a shallow hydrocarbon hotspot declining with depth." Uncited interpretive judgement not in FACTS; sidesteps that BH04 xylene increases with depth.
3. E2 S24 (PARTIAL): "These entries demonstrate that the duplicate results were not averaged or replaced by a selected result." Content is a FACTS note, but "demonstrate" asserts evidence the table does not provide.
(Borderline, scored SUPPORTED: E1 S5 / E2 S6 "applicable site criteria are taken from its SAND rows" - passage shows the rows, applicability comes from FACTS.)
