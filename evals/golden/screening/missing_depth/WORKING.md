# missing_depth: HSL analytes with no depth cannot pick a band

Site EV-10, criteria_set `hsl-a-b-vapour-intrusion`. Hand calculation, independent of screening.py.
Exceedance iff result (converted to criterion unit) > criterion strictly. ratio = result / criterion, half-up to 2 dp.

- ND-1 | Toluene 500 mg/kg : depth empty, HSL is depth-banded -> not_screened no_depth (never compared)
- ND-2 | Benzene 1 mg/kg : depth empty -> not_screened no_depth
- ND-3 | Benzene 1.0 mg/kg : depth 0.5 m, band 0 m to <1 m criterion 0.5: 1.0/0.5 = 2.00 exceedance
