# duplicate: parent and duplicate screened independently

Site EV-08, criteria_set `hil-a-residential`. Hand calculation, independent of screening.py.
Exceedance iff result (converted to criterion unit) > criterion strictly. ratio = result / criterion, half-up to 2 dp.

- BH01-0.5 | Lead 350 mg/kg : 350 > 300 -> 350/300 = 1.1667 -> 1.17 exceedance
- BH01-0.5-DUP | Lead 330 mg/kg : duplicate of BH01-0.5; 330 > 300 -> 1.10 exceedance, kept separate (not averaged, not worst-of)
- BH01-0.5 | Arsenic 50 mg/kg : parent 50 vs 100 -> below
- BH01-0.5-DUP | Arsenic 120 mg/kg : duplicate 120 > 100 -> 1.20 exceedance although parent is clean
