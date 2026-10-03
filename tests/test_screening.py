"""Screening edge cases asserted on the committed synthetic demo data (docs/03-data.md)."""
import pytest

from site_assess.screening import list_criteria_sets, load_sites, screen

HIL_A, HIL_D, HSL = "hil-a-residential", "hil-d-commercial", "hsl-a-b-vapour-intrusion"


def ex(result, sample, analyte):
    return next((e for e in result["exceedances"] if e["sample_id"] == sample and e["analyte"] == analyte), None)


def ns(result, sample, analyte):
    return [n["reason"] for n in result["not_screened"] if n["sample_id"] == sample and n["analyte"] == analyte]


def test_criteria_set_ids_and_sites():
    assert [c["id"] for c in list_criteria_sets()] == [HIL_A, HIL_D, HSL]
    assert all(c["source"]["doc_id"] == "nepm-asc-b1" for c in list_criteria_sets())
    assert [s["site_id"] for s in load_sites()] == ["DEMO-01", "DEMO-02", "DEMO-03"]
    assert all(len(s["client_name"].split()) > 1 for s in load_sites())


def test_demo01_clean_below_lor_unknown_exactly_equal():
    r = screen("DEMO-01", HIL_A)
    assert r["exceedances"] == []
    assert ns(r, "S03", "Cadmium") == ["below_lor"]
    assert ns(r, "S01", "Antimony") == ["no_criterion"]
    assert r["analytes_screened"] == 9 and r["samples_screened"] == 4  # S04 lead == criterion was compared, not flagged


def test_demo02_hotspot_depth_bands_and_boundaries():
    r = screen("DEMO-02", HSL)
    assert ex(r, "BH01-0.5", "Benzene")["ratio"] == 4.0
    assert ex(r, "BH01-0.5", "Benzene")["source"] == {"doc_id": "nepm-asc-b1", "page": 60, "table": "Table 1A(3)"}
    assert ex(r, "BH01-1.5", "F1")["criterion"] == 70.0  # band 1 m to <2 m, not the 0-1 m value
    assert ex(r, "BH01-3.0", "Benzene") is None and ex(r, "BH01-4.5", "Benzene") is None
    assert ns(r, "BH01-1.5", "Ethylbenzene") == ["non_numeric_criterion"]  # NL in the 1 m to <2 m band
    # same result either side of a band boundary: over just above it, under at the boundary (lower bound inclusive)
    for above, at in (("BH04-0.99", "BH04-1.00"), ("BH04-1.99", "BH04-2.00"), ("BH04-3.99", "BH04-4.00")):
        assert ex(r, above, "Xylenes") is not None, above
        assert ex(r, at, "Xylenes") is None, at
    assert ns(r, "BH06-ND", "Toluene") == ["no_depth"]


def test_demo02_unit_conversion_just_over_exactly_equal_duplicate_lor_above_criterion():
    r = screen("DEMO-02", HSL)
    e = ex(r, "BH03-0.5", "Naphthalene")
    got = (e["result"], e["unit"], e["criterion"], e["criterion_unit"], e["ratio"])
    assert got == (4500.0, "ug/kg", 3.0, "mg/kg", 1.5)
    assert ex(r, "BH05-0.5", "Benzene")["ratio"] == 1.2  # one reporting increment over
    assert ex(r, "BH05-0.5", "Toluene") is None and not ns(r, "BH05-0.5", "Toluene")  # equal: compared, not flagged
    assert ex(r, "BH01-0.5", "Toluene") and ex(r, "BH01-0.5-D", "Toluene") is None  # duplicate screened on its own
    assert ex(r, "BH01-0.5-D", "Benzene")
    assert ns(r, "BH02-0.5", "Benzene") == ["below_lor"]  # LOR 1.0 > criterion 0.5, still not an exceedance
    assert any("Duplicate" in n for n in r["notes"])


def test_demo03_alias_unit_mismatch_just_over_and_criteria_set_changes_result():
    a = screen("DEMO-03", HIL_A)
    assert len([e for e in a["exceedances"] if e["sample_id"] == "FILL-02"]) == 6
    assert ex(a, "FILL-02", "Mercury (inorganic)")["ratio"] == 1.3  # lab said "Mercury": alias matched
    assert ex(a, "FILL-03", "Lead")["ratio"] == 1.02
    assert ns(a, "FILL-04", "Lead") == ["unit_mismatch"]
    assert ex(a, "FILL-04", "Lead") is None
    d = screen("DEMO-03", HIL_D)
    assert d["exceedances"] == [] and ns(d, "FILL-04", "Lead") == ["unit_mismatch"]


def test_deterministic_and_sorted():
    for site, cs in (("DEMO-01", HIL_A), ("DEMO-02", HSL), ("DEMO-03", HIL_A)):
        r = screen(site, cs)
        assert r == screen(site, cs)
        keys = [(e["sample_id"], e["analyte"]) for e in r["exceedances"]]
        assert keys == sorted(keys)


@pytest.mark.parametrize("site,cs", [
    ("NOPE", HIL_A),            # unknown site
    ("DEMO-01", "nope"),        # unknown set
    ("DEMO-01", "aliases"),     # not a criteria set
    ("DEMO-03", HSL),           # HSL sand set, clay site
])
def test_value_errors(site, cs):
    with pytest.raises(ValueError):
        screen(site, cs)


def test_land_use_contradiction(monkeypatch):
    import site_assess.screening as s
    site = {"site_id": "DEMO-01", "land_use": "commercial-d", "soil_type": "sand"}
    monkeypatch.setattr(s, "load_sites", lambda: [site])
    with pytest.raises(ValueError, match="contradicts"):
        s.screen("DEMO-01", HIL_A)
