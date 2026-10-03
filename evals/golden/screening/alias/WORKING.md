# alias: lab spellings resolved via aliases.csv; unrecorded spelling is not matched

Site EV-12, criteria_set `hil-a-residential`. Hand calculation, independent of screening.py.
Exceedance iff result (converted to criterion unit) > criterion strictly. ratio = result / criterion, half-up to 2 dp.

- A1 | Cr(VI) 150 mg/kg : alias Cr(VI) -> Chromium (VI), HIL A 100: 150/100 = 1.50 exceedance (reported under canonical name; assumption)
- A2 | Inorganic Mercury 60 mg/kg : alias -> Mercury (inorganic), HIL A 40: 60/40 = 1.50 exceedance
- A3 | BaP TEQ 6 mg/kg : alias -> Carcinogenic PAHs (as BaP TEQ), HIL A 3: 6/3 = 2.00 exceedance
- A4 | Hexavalent Chromium 50 mg/kg : alias -> Chromium (VI), 50 < 100 -> no exceedance
- A5 | Hex Chrome 500 mg/kg : spelling not in aliases.csv and not a canonical name -> not_screened no_criterion
