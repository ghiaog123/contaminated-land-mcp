# hsl_depth_bands: samples either side of each depth-band boundary (lower-inclusive, upper-exclusive), sand

Site EV-09, criteria_set `hsl-a-b-vapour-intrusion`. Hand calculation, independent of screening.py.
Exceedance iff result (converted to criterion unit) > criterion strictly. ratio = result / criterion, half-up to 2 dp.

- D0.99 | Toluene 200 mg/kg : 0.99 m is in 0 m to <1 m (160): 200/160 = 1.25 exceedance
- D1.00 | Toluene 200 mg/kg : 1.0 m is in 1 m to <2 m (220), not the band below: 200 < 220 -> no exceedance
- D1.99 | Toluene 230 mg/kg : 1.99 m in 1 m to <2 m (220): 230/220 = 1.04545 -> 1.05 exceedance
- D2.00 | Toluene 230 mg/kg : 2.0 m in 2 m to <4 m (310): 230 < 310 -> no exceedance
- D3.99 | Toluene 320 mg/kg : 3.99 m in 2 m to <4 m (310): 320/310 = 1.03226 -> 1.03 exceedance
- D4.00 | Toluene 500 mg/kg : 4.0 m in 4 m+ (540): 500 < 540 -> no exceedance
- D4.50 | Toluene 600 mg/kg : 4.5 m in 4 m+ (540): 600/540 = 1.1111 -> 1.11 exceedance
