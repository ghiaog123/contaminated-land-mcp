# Manual grades: DEMO-01 drafts (epochs 1-3)

Scoring: SUPPORTED=1, PARTIAL=0.5, else 0. Rule-5 sentence ("exceedances are screening results ... do not by themselves establish risk") appears uncited in epochs 2 and 3; SYSTEM rule 5 tells the drafter to say it and cite only if a passage does. Graded SUPPORTED(rule 5) there, with the alternative score (PARTIAL) given too.

## Epoch 1
| n | cites | verdict | reason |
|---|---|---|---|
| 1 | - | SUPPORTED | client, site, address, land use, soil in FACTS |
| 2 | - | SUPPORTED | criteria_set in FACTS |
| 3 | p57:0161 | SUPPORTED | "HIL A Residential with garden/accessible soil" |
| 4 | - | SUPPORTED | counts + note 4 |
| 5 | - | SUPPORTED | exceedances none; story says clean residential lot |
| 6 | - | SUPPORTED | story: below-LOR and unknown rows listed, not hidden |
| 7 | - | UNSUPPORTED | "Schedule B1 characterizes HILs as conservative, generic assessment criteria used in first-stage screening for potential human-health risks." Claim about guidance, uncited; it paraphrases the p12 passage and should have carried the citation. |
| 8 | p12:0023 | PARTIAL | "an exceedance is a screening result against a criterion and does not by itself establish risk". Passage supports Tier-1 screening/conservative; it never says an exceedance does not establish risk (that is rule 5's wording, imported as if cited). |
| 9 | - | SUPPORTED | note 1 |
| 10 | - | SUPPORTED | note 2 |
| 11 | - | SUPPORTED | note 3 |

Table: 5 rows match FACTS exactly (S01 Antimony no_criterion; S01/S02/S04 PAH below_lor; S03 Cd below_lor). No numbers beyond FACTS.

claim_support = (1 + 0.5) / 2 = 0.75 (2 cited)
facts_support = 8 / 9 = 0.889 (9 uncited)

## Epoch 2
| n | cites | verdict | reason |
|---|---|---|---|
| 1 | - | SUPPORTED | FACTS |
| 2 | - | SUPPORTED | land use, soil, story |
| 3 | - | SUPPORTED | criteria_set |
| 4 | p57:0161 | SUPPORTED | HIL A passage |
| 5 | p12:0023 | SUPPORTED | "scientifically based, generic ... first stage ... chronic exposure ... intentionally conservative" all present |
| 6 | - | SUPPORTED (rule 5) | "does not by itself establish risk" is not in FACTS; mandated by rule 5, uncited. If treated strictly: PARTIAL. |
| 7 | - | SUPPORTED | exceedances none |
| 8 | - | SUPPORTED | note 1 |
| 9 | - | SUPPORTED | counts + note 4 |
| 10 | - | SUPPORTED | follows from exceedances: none |
| 11 | - | SUPPORTED | table lead-in |
| 12 | - | SUPPORTED | note 2 |
| 13 | - | SUPPORTED | story + not_screened reasons |
| 14 | - | SUPPORTED | note 3 |
| 15 | - | SUPPORTED | note 3 |
| 16 | - | SUPPORTED | note 5 (1.0 m, "1 m to <2 m" in FACTS) |

Table matches FACTS. Numbers all in FACTS.

claim_support = 2 / 2 = 1.0
facts_support = 14 / 14 = 1.0 (strict on S6: 13.5 / 14 = 0.964)

## Epoch 3
| n | cites | verdict | reason |
|---|---|---|---|
| 1 | - | SUPPORTED | FACTS |
| 2 | - | SUPPORTED | FACTS |
| 3 | p57:0161 | SUPPORTED | HIL A passage |
| 4 | p12:0023 | SUPPORTED | first stage screening, chronic exposure, intentionally conservative, reasonable worst-case scenario all in passage |
| 5 | - | SUPPORTED | counts + note 4 |
| 6 | - | SUPPORTED | exceedances none |
| 7 | - | SUPPORTED | note 1 |
| 8 | - | SUPPORTED | note 3 |
| 9 | - | SUPPORTED | note 5 (truncated, no added claim) |
| 10 | - | SUPPORTED (rule 5) | same as epoch 2 S6; strict: PARTIAL |
| 11 | - | SUPPORTED | follows from note 4 and the not-screened rows |
| 12 | - | SUPPORTED | table lead-in |
| 13 | - | SUPPORTED | note 2 |
| 14 | - | SUPPORTED | Antimony is no_criterion, others below_lor; sound inference, not a verdict |

Table matches FACTS. No extra numbers.

claim_support = 2 / 2 = 1.0
facts_support = 12 / 12 = 1.0 (strict on S10: 11.5 / 12 = 0.958)

## Section-level checks
| check | E1 | E2 | E3 |
|---|---|---|---|
| all exceedances covered (none exist; stated) | yes | yes | yes |
| all 5 not-screened items covered | yes | yes | yes |
| numbers not in FACTS | none | none | none |
| compliance/safety verdict | none | none | none |
| editability | Best: table gives per-row treatment, reads like a report. One bad cited sentence and one uncited guidance sentence to fix. | Clean, a little repetitive (exceedance/LOR points said twice). Needs almost no rewrite. | Clean, adds a useful "no comparison for Antimony/below-LOR" clarification; no mention of clean-site story. Needs almost no rewrite. |

## Cross-epoch patterns
- The two cited passages (p57 HIL A definition, p12 HIL screening) are used faithfully in 5 of 6 cited sentences. The only failure is E1 S8, which attaches the rule-5 "does not establish risk" statement to p12, which does not say it. Epochs 2 and 3 correctly leave that sentence uncited.
- E1 S7 puts a guidance claim in an uncited sentence (the p12 content, citation omitted). E2 and E3 cited the equivalent content correctly.
- No numbers, verdicts or invented thresholds in any draft; every note from FACTS is restated faithfully. E2 is wordiest (16 sentences, 6558 output tokens vs ~3200-3450).
- The rule-5 sentence is a grading ambiguity: SYSTEM requires it but it is neither in FACTS nor in a passage. Treat it as a process statement or tighten the rubric.
- Rule 7 (a cited sentence on what passages say about the criterion/next steps) is met only by definitions of HIL A and HIL screening; none of the drafts cite guidance on below-LOR or no-criterion handling (no such passage was supplied).

Ranking: E3 ~ E2 > E1 on strict support.

## Worst 3 sentences
1. E1 S8: "Under this screening framework, an exceedance is a screening result against a criterion and does not by itself establish risk [nepm-asc-b1:p12:0023]." PARTIAL; the passage says nothing about exceedances or risk not being established.
2. E1 S7: "Schedule B1 characterizes HILs as conservative, generic assessment criteria used in first-stage screening for potential human-health risks." UNSUPPORTED as written; an uncited claim about what guidance says.
3. E2 S6 / E3 S10 (tie, only under strict reading): "does not by itself establish risk" stated uncited; supported only by SYSTEM rule 5, not by FACTS or a passage.
