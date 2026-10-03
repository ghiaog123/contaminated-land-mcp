# unconvertible_unit: units outside the mass-fraction conversion table

Site EV-04, criteria_set `hil-a-residential`. Hand calculation, independent of screening.py.
Exceedance iff result (converted to criterion unit) > criterion strictly. ratio = result / criterion, half-up to 2 dp.

- S1 | Lead 500 mg/L : mg/L is a volumetric concentration, not convertible to mg/kg -> not_screened unit_mismatch (never compared, even though 500 > 300)
- S1 | Nickel 500 uS/cm : uS/cm is conductivity -> not_screened unit_mismatch
- S1 | Arsenic 50 mg/kg : mg/kg, 50 vs 100 -> below, no exceedance
