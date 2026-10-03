# exactly_equal: result equal to the criterion is not an exceedance

Site EV-05, criteria_set `hil-a-residential`. Hand calculation, independent of screening.py.
Exceedance iff result (converted to criterion unit) > criterion strictly. ratio = result / criterion, half-up to 2 dp.

- S1 | Arsenic 100 mg/kg : 100 mg/kg vs 100 -> equal, not an exceedance
- S1 | Cadmium 20000 ug/kg : 20000 ug/kg = 20 mg/kg vs 20 -> equal after conversion, not an exceedance
- S1 | Lead 300.0 mg/kg : 300.0 vs 300 -> equal, not an exceedance
- S1 | Mercury (inorganic) 40 mg/kg : 40 vs 40 -> equal, not an exceedance
