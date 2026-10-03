from contaminated_land.drafting import check_numbers, validate_citations

P = [
    {
        "chunk_id": "nepm-asc-b1:p12:0003",
        "doc_id": "nepm-asc-b1",
        "doc_title": "t",
        "page": 12,
        "section": None,
        "text": "x",
        "score": 1.0,
    }
]


def test_valid_citation():
    assert validate_citations("Lead exceeds the HIL [nepm-asc-b1:p12:0003].", P) == []


def test_unknown_id_rejected():
    errs = validate_citations("Claim [nepm-asc-b1:p99:0001] and ok [nepm-asc-b1:p12:0003].", P)
    assert len(errs) == 1 and "p99" in errs[0]


def test_malformed_ids_rejected_and_plain_brackets_ignored():
    assert len(validate_citations("Claim [nepm-asc-b1:p12].", P)) == 1
    assert len(validate_citations("Claim [nepm-asc-b1:p12:0003, other:p1:0001].", P)) == 1  # multi-cite checked per id
    assert validate_citations("See [the table](http://x) and [note] here.", P) == []


S = {
    "site_id": "DEMO-001",
    "criteria_set": "hil-a",
    "samples_screened": 12,
    "analytes_screened": 20,
    "exceedances": [
        {
            "sample_id": "BH01-0.5",
            "depth_m": 0.5,
            "analyte": "Lead",
            "result": 1200.0,
            "unit": "mg/kg",
            "criterion": 300.0,
            "criterion_unit": "mg/kg",
            "ratio": 4.0,
            "source": {"doc_id": "nepm-asc-b1", "page": 12, "table": "Table 1A(1)"},
        }
    ],
    "not_screened": [],
    "notes": [],
}


def test_numbers_pass_with_normalisation():
    md = (
        "BH01-0.5 at 0.50 m: Lead 1,200 mg/kg vs 300.0 mg/kg, ratio 4.00 "
        "across 1 exceedance of 12 samples [nepm-asc-b1:p12:0003]."
    )
    assert check_numbers(md, S) == []


def test_invented_number_fails():
    errs = check_numbers("Lead was 120 mg/kg, ratio 4.", S)
    assert errs == ["number 120 does not appear in the screening output"]


def test_ids_placeholders_and_list_markers_ignored():
    assert check_numbers("1. <SITE_1> and DEMO-001 and BH01-0.5 [a:p9:0001]", S) == []
