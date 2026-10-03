# mixed: commercial HIL with every outcome in one site

Site EV-13, criteria_set `hil-d-commercial`. Hand calculation, independent of screening.py.
Exceedance iff result (converted to criterion unit) > criterion strictly. ratio = result / criterion, half-up to 2 dp.

- M1 | Arsenic 3000 mg/kg : HIL D 3000: equal -> no exceedance
- M1 | Cadmium 901 mg/kg : HIL D 900: 901/900 = 1.00111 -> 1.00 exceedance
- M1 | Lead 2000 mg/kg <: qualifier <, LOR 2000 > HIL D 1500 -> below_lor
- M2 | Nickel 7000000 ug/kg : 7000000 ug/kg = 7000 mg/kg; HIL D 6000: 7000/6000 = 1.1667 -> 1.17 exceedance
- M2 | Zinc 5 mg/L : mg/L -> unit_mismatch
- M2 | Toluene 1 mg/kg : not in hil-d-commercial -> no_criterion
- M3 | Hexavalent Chromium 3601 mg/kg : alias -> Chromium (VI), HIL D 3600: 3601/3600 = 1.00028 -> 1.00 exceedance
- M3 | Copper 300000 mg/kg : HIL D 240000: 300000/240000 = 1.25 exceedance
- M3-DUP | Copper 200000 mg/kg : duplicate of M3; 200000 < 240000 -> no exceedance
