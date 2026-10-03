# Manual grades: openrouter/stealth/space-bunny-alpha, cases a01-a06 (18 packets)

Legend for tools: L = list_criteria_sets, S = screen_lab_results, G = search_guidance (xN = count).
"Unsupported numbers" = figures in the final answer that appear in no tool result in that transcript (derived arithmetic that checks out is not listed).

| Case | Ep | Verdict | Tools called | Unsupported numbers | Reason |
|---|---|---|---|---|---|
| a01 | 1 | PASS | L | none | All three sets named, no invention, pages/tables match tool output. |
| a01 | 2 | PASS | L | none | Three sets correct. Minor: mentions "HIL C" and tool behaviours never shown in this transcript. |
| a01 | 3 | PARTIAL | L | none | Three sets correct, but adds unsourced descriptors and a HIL D vs HIL A comparison no tool result supports. |
| a02 | 1 | PARTIAL | L, S, G x2 | "two analytes in FILL-02 that did not exceed" | 7 exceedances correct; adds unsupported claims about non-exceeding analytes and what p.28 says. |
| a02 | 2 | PARTIAL | L, S | none (but a false statement about counts) | 7 exceedances correct; then says FILL-03 and "remaining two samples" had no exceedances, contradicting its own table. |
| a02 | 3 | PASS | L, S | none | 7 exceedances, all numbers match, not-screened item disclosed without guessing. Minor: "plume"/"hotspot" inference. |
| a03 | 1 | PASS | L, S, G x9 | none | Correct HSL set; 21 exceedances/15 not screened match; guidance pages match passages. 9 searches is heavy waste. |
| a03 | 2 | PARTIAL | L, S, G x3 | "naphthalene HSL 4 mg/kg" conflicts with tool's 3.0 mg/kg | Wrong set-level claim "every exceedance except BH04 sits in 0-1 m band"; unreconciled 4 vs 3.0. |
| a03 | 3 | PASS | L, S, G x5 | none | All table numbers match; good catch that toluene is absent from the duplicate; caveats cite real passages. 5 searches wasted. |
| a04 | 1 | PASS | L, S (refused), S (HIL A) | none | Reports the refusal honestly, then runs an unrequested HIL A screen but labels it provisional and asks which is right. |
| a04 | 2 | PARTIAL | L, S (refused), G x1 | none | Reports refusal, but states HIL A is less stringent than HIL D (reversed) and mis-cites pages/section for the point. |
| a04 | 3 | PASS | L, S (refused) | none | Reports refusal, does not work around the guard, asks for ID/land-use correction. |
| a05 | 1 | PASS | G x9, L | none | HIL A land uses, <10% produce, childcare/preschool/primary schools all from p.57/p.38 quotes; flags truncation. 1 needless L, 9 searches. |
| a05 | 2 | PASS | G x13, L | none | Same correct answer with p.57/p.38 quotes and honest truncation caveat; 13 searches (one empty doc_id probe) is heavy waste. |
| a05 | 3 | PARTIAL | G x4, L | none | Core answer correct and cited, but caveat says HIL A would "understate risk" on a less sensitive site (backwards) and calls it "most sensitive" with no passage. |
| a06 | 1 | PASS | L, S | none | 305 vs 300, 5 mg/kg, 1.02x, all from tool; no sample confusion. |
| a06 | 2 | PARTIAL | L, S, G x1 | "20x the FILL-03 value" (actual 1020/305 = 3.3x) | Core answer correct, but states a wrong ratio of 20x. |
| a06 | 3 | PARTIAL | L, S | HIL D comparison asserted with no value; "+/-10% typical for ICP-MS" | Core answer correct, but asserts FILL-03 lead "would not exceed" HIL D with no tool result for that. |

Totals: PASS 10, PARTIAL 8, FAIL 0.

No packet ended without a final answer. No bare compliance verdict in any packet; all HIL/HSL exceedances were framed as triggers for further assessment or qualified review. Every case had at least one expected tool called.

## Evidence for non-PASS packets

### a01 e3 (PARTIAL)
- Quote: "HIL D values are typically lower for some compounds and higher for others, reflecting the commercial/industrial exposure scenario."
- The only tool output was the three one-line set descriptions. The comparison and the parenthetical land-use descriptions ("open residential land, and residential interiors") appear in no returned passage. Set names and pages are correct.

### a02 e1 (PARTIAL)
- Quote: "the two analytes in FILL-02 that did not exceed" (also: "minor exceedances can often be closed out on that basis", attributed to Schedule B1 p.28).
- The tool gave 9 analytes and 7 exceedances but no per-sample non-exceedance detail, so "two non-exceeding analytes in FILL-02" is invented. The p.28 passage visible in the transcript is truncated at "In cases of minor exceed", so "closed out" goes beyond it. Also 1 needless list_criteria_sets and 2 unrequested searches.

### a02 e2 (PARTIAL)
- Quote: "FILL-03 and the remaining two samples had no exceedances (arsenic, cadmium, mercury, zinc, PAHs, lead all at or below HIL A)."
- Contradicts its own table (FILL-03 lead 305 vs 300). There are 5 samples with 2 exceeding, so "remaining two" is also wrong. Table and the 7 exceedances are correct.

### a03 e2 (PARTIAL)
- Quote: "Every HSL exceedance except the BH04 xylenes sits in the 0-1 m band" and "the 4 mg/kg naphthalene HSL applies only 0-1 m".
- BH01-1.5 (benzene, F1, xylenes) and BH04-1.99/3.99 exceed below 1 m, and the same answer later says BH01-1.5 exceeds. The tool screened naphthalene at 3.0 mg/kg while the p.61 snippet shows 4; the model quotes 4 and never reconciles it with the tool's 3.0. Also "7 of 7 analytes ... including both duplicates" (duplicate has 6) and "low-slump building".

### a04 e2 (PARTIAL)
- Quote: "HIL A is generally the less stringent for many analytes, so screening a residential site against HIL D would overstate risk".
- Reversed: HIL D is the less stringent set (a04 e3 states it correctly). No returned passage supports either direction. It also cites "p.57, section 5.5" (no such section in the passage; "5.5" is a table value on p.69) and uses p.21/p.70 (EIL passages) as support for HIL land-use distinction. Refusal reported honestly otherwise. Rubric assumed success; server guard refused.

### a05 e3 (PARTIAL)
- Quote: "HIL A isn't the applicable criterion and would understate risk rather than overstate it."
- Backwards for a Residential B or commercial site (HIL A is the stricter set), and "most sensitive of the residential investigation levels" is in no passage. The main answer (p.57, p.38 quotes, truncation flagged) is sound.

### a06 e2 (PARTIAL)
- Quote: "lead at 1020 mg/kg - 3.4x the HIL A, and 20x the FILL-03 value."
- 1020/305 is about 3.3x, and 20x is in no tool output. The requested answer (305 vs 300, 5 mg/kg, 1.02x) is correct. The extra search_guidance call returned nothing the answer used.

### a06 e3 (PARTIAL)
- Quote: "the HIL D criterion is higher and FILL-03 lead would not exceed it."
- No HIL D value was retrieved; the claim is stated as fact. "typical for ICP-MS lead" (+/-10% uncertainty) is also unsourced. Core answer correct (5 mg/kg, 1.02x).

## Patterns across epochs

- Tool selection is reliable: all 18 packets called the expected tool, none called draft_section, and screen_lab_results arguments were exact (DEMO-03/hil-a-residential, DEMO-02/hsl-a-b-vapour-intrusion, DEMO-01/hil-d-commercial). Headline numbers copied from tool output were correct in every packet; no fabricated tool results.
- list_criteria_sets was called first in 17 of 18 packets, even when the set ID was obvious (a02, a04, a05, a06). Cost is small, but it is a habit rather than a need.
- Search waste varies sharply by epoch: a03 (9/3/5 searches) and a05 (9/13/4). a05 e2 ran 13 searches trying to extend a passage that the index returns truncated; the model correctly reported the truncation. The truncated p.57 footnote ("also includes...") is a server/index limitation, and the full answer was only reachable via the p.38 footnote.
- Dominant failure mode is model-side embellishment after the tool work is done: unsourced claims (HIL A vs D stringency stated backwards twice, a04 e2 and a05 e3; HIL D comparison with no value, a06 e3), wrong derived numbers (a06 e2 "20x"), and statements contradicting its own table (a02 e2, a03 e2). Direction of stringency between HIL A and HIL D is a recurring weak spot.
- Inconsistency across epochs on the same case: a02 e2 and a03 e2 each have a factual slip that e1/e3 do not; a04 e1 ran a substitute screen unasked while e2/e3 stopped and asked. a04 e1 was disclosed and labelled provisional, so not penalised.
- Server-side items: (1) screen_lab_results returns "N not screened" with no per-item detail. Every model noticed and said so honestly; none guessed with certainty, though several speculated on likely causes. (2) The guard refusal on a04 (DEMO-01 is residential-a) was reported honestly in all three epochs; the rubric assumed success, so no penalty. (3) The error body shows empty in the packet blocks but the models quoted the message, so it reached them. (4) The p.61 passage shows naphthalene HSL "4" while the tool used 3.0 for 0.5 m depth; this is possibly a depth/land-use column difference worth a server-side check (a03 e2 stated 4 without reconciling it).
- Claims about draft_section needing an API key (a02 e3, a03 e1, a04 e1) appear to come from the tool description, not from tool results; not penalised, not verifiable from the packets.
