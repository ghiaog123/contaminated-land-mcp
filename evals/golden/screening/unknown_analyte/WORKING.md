# unknown_analyte: analytes absent from the criteria set

Site EV-03, criteria_set `hil-a-residential`. Hand calculation, independent of screening.py.
Exceedance iff result (converted to criterion unit) > criterion strictly. ratio = result / criterion, half-up to 2 dp.

- S1 | Atrazine 5 mg/kg : no row named Atrazine in hil-a-residential -> not_screened no_criterion
- S1 | Pyrene 3 mg/kg : no row named Pyrene in hil-a-residential -> not_screened no_criterion
- S1 | Lead 100 mg/kg : 100 vs 300 -> below, no exceedance
