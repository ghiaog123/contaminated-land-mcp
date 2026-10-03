# below_lor: non-detects, including LOR above the criterion

Site EV-01, criteria_set `hil-a-residential`. Hand calculation, independent of screening.py.
Exceedance iff result (converted to criterion unit) > criterion strictly. ratio = result / criterion, half-up to 2 dp.

- S1 | Arsenic 150 mg/kg <: qualifier <, value is the LOR 150, which exceeds HIL A 100. Never an exceedance -> not_screened below_lor
- S1 | Lead 0.5 mg/kg <: qualifier <, LOR 0.5 (well under 300) -> not_screened below_lor
- S1 | Cadmium 25 mg/kg : detect, 25 vs HIL A 20 -> 25/20 = 1.25 exceedance
