# non_numeric_criterion: NL (not limiting) cells are never compared

Site EV-11, criteria_set `hsl-a-b-vapour-intrusion`. Hand calculation, independent of screening.py.
Exceedance iff result (converted to criterion unit) > criterion strictly. ratio = result / criterion, half-up to 2 dp.

- NL-1 | Ethylbenzene 500 mg/kg : 1.5 m -> 1 m to <2 m row has empty criterion (NL) -> not_screened non_numeric_criterion
- NL-2 | Naphthalene 100 mg/kg : 2.5 m -> 2 m to <4 m row is NL -> non_numeric_criterion
- NL-3 | F2 1000 mg/kg : 5.0 m -> 4 m+ row is NL -> non_numeric_criterion
- NL-4 | Ethylbenzene 60 mg/kg : 0.5 m -> 0 m to <1 m row is 55: 60/55 = 1.0909 -> 1.09 exceedance
- NL-5 | F2 500 mg/kg : 3.0 m -> 2 m to <4 m row is 440: 500/440 = 1.1364 -> 1.14 exceedance
