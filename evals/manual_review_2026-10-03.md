# Manual review, 2026-10-03

Every case from the 2026-10-03 rerun was graded by reading, not by an LLM judge. The owner asked for this because a
flash-lite judge was not trusted. Graders were Claude Sonnet subagents working from per-case packets (full tool
results, full passage text, the FACTS block); the main agent then re-checked a sample of their verdicts against the
source. **This review is not independent:** the same agent family built the system, wrote the agent cases and graded
them. Read it as a careful self-review with evidence, not as an external audit.

Models: everything under test ran on `stealth/space-bunny-alpha` (free). No paid model was used for grading.

## Summary

| Area | Automatic metric | Manual grade |
|---|---|---|
| Screening (13 cases) | 13/13 exact | not regraded (expected outputs are hand-computed already) |
| PII leak (offline, real retrieval, real model) | 0 leaks, round trip 1.0 | not regraded |
| Retrieval (20 questions, hybrid) | recall@5 0.85, MRR 0.80 | 17 answered, 1 partial, 2 not answered |
| Drafts (3 sites x 3 draws) | citation validity 1.0, number fidelity 1.0 | cited sentences supported 54/56 (0.96); uncited sentences supported by FACTS 124/127 (0.98) |
| Agent tool use, run 1 (12 cases x 3 draws) | 36/36 correct tool and arguments | 22 PASS, 13 PARTIAL, 1 FAIL |
| Agent tool use, run 2 (after server fixes 1 and 2) | 36/36; mean tool calls 4.31 (run 1: 5.03); 0 step-cap hits (run 1: 1) | 18 PASS, 16 PARTIAL, 2 FAIL |
| a09 rerun (after fix 3) | 3/3 | 3 PASS (run 2: 1 PASS, 2 FAIL) |
| a09 on final code (after fixes 3 and 4) | 3/3 | 3 PASS |

PARTIAL counts 0.5 in the draft ratios. The graders' per-sentence and per-case tables, with quoted evidence, are in
[manual_review_2026-10-03/](manual_review_2026-10-03/). The packets they read (full transcripts) are not committed;
they are regenerated from the inspect logs with `evals/extract_agent.py`.

## Drafts

| Site | Draw | Cited supported | Uncited supported |
|---|---|---|---|
| DEMO-01 | 1 / 2 / 3 | 0.75 / 1.00 / 1.00 | 0.89 / 1.00 / 1.00 |
| DEMO-02 | 1 / 2 / 3 | 0.96 / 1.00 / 1.00 | 1.00 / 0.95 / 1.00 |
| DEMO-03 | 1 / 2 / 3 | 0.93 / 1.00 / 0.92 | 1.00 / 0.93 / 1.00 |

- No CONTRADICTED sentence, no number outside FACTS, no compliance or safety verdict in any of the 9 drafts. Every
  exceedance and every not-screened item is covered in every draft (DEMO-02: 21 exceedances across HSL depth bands,
  all band criteria checked).
- The typical defect is a strengthened paraphrase: the passage says exceedances "trigger consideration", the draft
  says "should be considered" or "as the response". Second most common: an uncited sentence about what guidance
  means.
- Rule 7 (one cited sentence per exceedance group) produces filler: the same passage restated two or three times,
  or a worked example from another site cited as if it were general guidance.
- These drafts were made before fix 4, when the site `story` was still in FACTS. DEMO-03 drafts repeat its
  "a second run on the commercial HIL changes the result" line; the graders scored it as supported by FACTS, which
  it was, but the fact itself was wrong to supply.
- The earlier flash-lite judge reported claim_support 0.933 and facts_support 0.825 on a single draw. Manual grading
  of 9 new draws is higher (0.96 / 0.98). The two were not run on the same drafts, so this is not an agreement rate.

## Retrieval

- Agreement with the automatic metric: same count (17), different sets. r03 is an automatic hit whose gold chunk
  holds only footnotes; r06 is an automatic miss where a rank-5 passage on another page names the right table.
- r02 and r11 are ranking failures with a sound gold page. r02 (Table 1A(3)) is numeric cells with little lexical
  or semantic hook; r11's enumerated list ranks 14 behind narrative and table-of-contents chunks.
- Noise chunks (tables of contents, reference lists, glossary, empty templates) take top-5 slots in about 9 of 20
  questions; in r19, 4 of 5.
- Narrative questions are strong: 10 of 11 answered at rank 1. Table lookups remain the weak spot.

## Agent tool use (run 1)

Tool choice and arguments were right in all 36 transcripts; headline numbers were copied correctly from tool
results; tool errors were reported honestly; no tool result was fabricated. The PARTIALs are model-side
embellishment after the tool call:

- stated facts the tools never returned (HIL A vs HIL D stringency stated backwards twice; "20x" for a 3.3x ratio;
  an invented "14 results");
- statements that contradict the model's own table;
- in the three-turn flow, the draft was relayed verbatim in 1 of 3 draws; the other two edited it and dropped
  citations;
- "Just give me yes or no": 2 of 3 draws open with a bare "No." before hedging.

The one FAIL (a12, draw 3) hit the 8-step cap after 14 searches with no answer.

## Agent tool use (run 2)

Same cases, same model, after fixes 1 and 2 below. Graded by a fresh pair of graders who read run 1's grades only
after grading run 2.

- What the fixes measurably changed: mean tool calls per case 5.03 to 4.31; guidance searches fell most where
  passages had been cut (a05 9.7 to 4.0, a12 10.3 to 6.7); no step-cap hit (a12 draw 3 failed on it in run 1 and
  answered after 6 searches in run 2); passages are now quoted whole; the invented "14 results" in a08 is gone now
  that not-screened rows are listed.
- What they did not change: model-side embellishment. Verdicts moved from 22/13/1 to 18/16/2 (PASS/PARTIAL/FAIL),
  but run 2's graders counted more strictly (exceedance counts, footnote attributions), so the verdict shift is not
  a like-for-like comparison. The counts above are the reliable signal.
- New FAILs, both a09 turn 3: draw 2 replaced the server's draft with its own text, dropped two of its citations,
  added nine the server never produced, and stated HIL B values (lead 450, arsenic 140 mg/kg) that appear in no
  tool result (the table says 1200 and 500). Draw 3 never showed the draft at all. Fix 3 below targets this.
- a11 ("just give me yes or no"): 3 of 3 draws open with "No". The model follows the user's format over the
  caution; the numbers and the follow-up advice are right.

## a09 rerun (after fix 3)

Case a09 only, 3 draws. Graded by the main agent with a script check (draft text found verbatim in the final answer,
citation sets compared, numbers in the answer looked up in earlier tool output) plus reading the commentary.

- 3 of 3 PASS: the draft is reproduced in full in every draw (run 2: 1 of 3), no citation dropped, no number that
  is not in an earlier tool result. Comments come after the draft. Draw 1 adds five citations, all in its own
  reviewer notes and all from passages it had retrieved in turn 2.
- The reviewer notes were useful and found fix 4: all three flagged the "commercial HIL changes the result" sentence
  as describing a run that does not exist.

## a09 on final code (after fixes 3 and 4)

Case a09 again, 3 draws, same checks. 3 of 3 PASS: draft reproduced in full, no citation dropped or added, no number
outside earlier tool output, comments after the draft. The "commercial HIL changes the result" sentence is gone from
all three drafts, and no draw read the restored client name as a redaction failure. This is the end-to-end check
for fix 4. The other 11 cases were not rerun on the final code; fixes 3 and 4 touch only the `draft_section`
description and the drafting FACTS, which only a09 exercises.

## Server-side findings

Fixed (1 and 2 after run 1, 3 after run 2, 4 after the a09 rerun; tests added for 1, 2 and 4):

1. `search_guidance` cut each passage to 200 characters in its text output. Hosts that pass only the text to the
   model (inspect did; many do) saw half sentences, which drove repeated searches (up to 16 in one case) and the
   step-cap FAIL. Now the full passage text is returned.
2. `screen_lab_results` text said "N not screened" without naming them. Now each not-screened row is listed with its
   reason, and exceedances show depth.

3. (after run 2) The `draft_section` tool description now tells the host to show the returned markdown unchanged,
   with its citations and warnings, comments after it, and no numbers of its own. Effect: see "a09 rerun" below.
4. (after the a09 rerun) `drafting._facts` passed the site's `story` field to the drafter. `story` in
   `data/lab/sites.yaml` is a developer note about the synthetic data ("A second run on the commercial HIL changes
   the result"), and drafts reported it as a finding about a run that never happened. All three a09 rerun draws
   flagged that sentence. `story` is no longer a fact. The tool description also now says names are restored in the
   returned draft, which two draws had read as a redaction failure.

Open, not fixed:

5. Continuation chunks of Table 1A(3) lose the soil-type label (SAND/SILT/CLAY sits in rows, not headers). The
   p.61 chunk shows naphthalene "4" with no soil type; one model read it as the criterion (the server correctly
   used 3 mg/kg for sand, 0 to <1 m, checked against the PDF). Fix: carry the current row-group label into every
   table chunk at ingest.
6. Remove or down-weight table-of-contents and reference-list chunks at ingest.
7. Synthetic DEMO-02 data: BH04 xylenes rise with depth, against the site story ("declining with depth"). The story
   no longer reaches drafts (fix 4), but the data and the story in `sites.yaml` should still be aligned.

Not a defect: the land-use guard accepts HIL D for DEMO-03 and refuses it for DEMO-01, because only DEMO-03
declares `also_screen_as: [commercial-d]`.

## Rubric notes

- a04 assumed HIL D screening of DEMO-01 would succeed; the server's land-use guard refuses it. Models were graded on
  handling the refusal. The case was not edited.

## Spot checks by the main agent

Ten grader verdicts were re-checked against the packets or the PDF. Run 1: the 20x ratio claim, the invented
section reference, the naphthalene value, the dropped citations in a09 draw 2. Drafts and retrieval: DEMO-01 draw 1
sentence 8, the DEMO-02 band criteria, the r19 noise chunks. Run 2: "five of the seven" in a02 draw 3, the invented
injection warning in a05 draw 2 (the model took the tool description for passage text), the HIL B values in a09
draw 2. All ten grader verdicts held. On the naphthalene case the grader suspected a
criteria error; the check showed the criterion is right and the chunk is the problem (finding 5).

## Regression check after all fixes

`pii_leak` offline and real (`stealth/space-bunny-alpha`): no_leak 1.0, round_trip / redacted_something 1.0.
`draft_faithfulness`, one draw per site, no judge: citation validity raw and final 1.0, number_fidelity 1.0, 0 removals,
0 retries. Full test suite: 93 passed. A grep of every log and packet directory for the key prefix found nothing.
