# ratio_half_up: ratio rounds half-up, not half-even and not binary-float

Site EV-07, criteria_set `hil-a-residential`. Hand calculation, independent of screening.py.
Exceedance iff result (converted to criterion unit) > criterion strictly. ratio = result / criterion, half-up to 2 dp.

- S1 | Zinc 8325 mg/kg : 8325/7400 = 1.125 exactly -> half-up 1.13 (banker's rounding would give 1.12)
- S1 | Cadmium 20.1 mg/kg : 20.1/20 = 1.005 exactly in decimal -> half-up 1.01 (float round() commonly gives 1.0)
- S1 | Copper 6090 mg/kg : 6090/6000 = 1.015 exactly -> half-up 1.02
