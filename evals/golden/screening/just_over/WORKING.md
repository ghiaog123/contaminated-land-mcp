# just_over: results marginally above the criterion: exceedance with ratio near 1

Site EV-06, criteria_set `hil-a-residential`. Hand calculation, independent of screening.py.
Exceedance iff result (converted to criterion unit) > criterion strictly. ratio = result / criterion, half-up to 2 dp.

- S1 | Lead 300.5 mg/kg : 300.5 > 300 -> exceedance; 300.5/300 = 1.00167 -> 1.00
- S1 | Arsenic 100.1 mg/kg : 100.1 > 100 -> exceedance; 1.001 -> 1.00
- S1 | Nickel 401 mg/kg : 401 > 400 -> exceedance; 401/400 = 1.0025 -> 1.00
- S1 | Cadmium 20.2 mg/kg : 20.2 > 20 -> exceedance; 20.2/20 = 1.01
