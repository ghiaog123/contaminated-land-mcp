# unit_conversion: ug/kg results converted to the mg/kg criterion unit

Site EV-02, criteria_set `hil-a-residential`. Hand calculation, independent of screening.py.
Exceedance iff result (converted to criterion unit) > criterion strictly. ratio = result / criterion, half-up to 2 dp.

- S1 | Lead 400000 ug/kg : 400000 ug/kg = 400 mg/kg; vs 300 -> 400/300 = 1.3333 -> 1.33 exceedance
- S1 | Zinc 8000000 ug/kg : 8000000 ug/kg = 8000 mg/kg; vs 7400 -> 8000/7400 = 1.0811 -> 1.08 exceedance
- S1 | Copper 5000000 ug/kg : 5000000 ug/kg = 5000 mg/kg; vs 6000 -> below, no exceedance (a missed conversion would read 5,000,000 and exceed)
