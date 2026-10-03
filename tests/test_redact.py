import pytest

from contaminated_land.redact import Redactor

SITES = [
    {"site_id": "DEMO-001", "client_name": "Acme Fuels Pty Ltd", "site_address": "12 Smith Road, Parramatta NSW 2150"},
    {"site_id": "DEMO-002", "client_name": "Brightwater Council", "site_address": "7 Quay Street, Newcastle NSW 2300"},
]
TEXT = (
    "Site DEMO-001 for Acme Fuels Pty Ltd at 12 Smith Road, Parramatta NSW 2150. "
    "Lead 120 mg/kg vs 100 mg/kg (ratio 1.2). Repeat: ACME FUELS PTY LTD; DEMO-001 again. Contact John Citizen."
)


@pytest.fixture(scope="module")
def red():
    return Redactor(SITES, keep=("Lead",))


def test_round_trip(red):
    out, mapping = red.redact(TEXT)
    assert red.restore(out, mapping) == TEXT


def test_exact_match_client_and_address(red):
    out, mapping = red.redact(TEXT)
    for secret in ("Acme Fuels", "ACME FUELS", "Smith Road", "Parramatta", "DEMO-001", "John Citizen"):
        assert secret not in out
    assert "<CLIENT_1>" in out and "<ADDRESS_1>" in out and "<SITE_1>" in out and "<PERSON_1>" in out
    assert mapping["<ADDRESS_1>"] == "12 Smith Road, Parramatta NSW 2150"


def test_numbers_untouched_and_same_value_same_placeholder(red):
    out, _ = red.redact(TEXT)
    for n in ("120", "100", "1.2"):
        assert n in out
    assert out.count("<SITE_1>") == 2  # DEMO-001 twice
    assert "Lead" in out  # keep list respected


def test_second_site_and_unknown_id_pattern(red):
    out, mapping = red.redact("DEMO-002 and ZZ-9 at Brightwater Council")
    assert "Brightwater" not in out and "DEMO-002" not in out and "ZZ-9" not in out
    assert len(mapping) == 3


def test_keep_is_whole_word_only():
    r = Redactor([], keep=("Benzene", "Mercury (inorganic)"))
    out, mapping = r.redact("Ben reviewed the Mercury results.")  # "ben" is a substring of "benzene"
    assert mapping == {"<PERSON_1>": "Ben"} and out.startswith("<PERSON_1>")
    assert "Mercury" in out
