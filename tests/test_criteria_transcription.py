"""Every criteria row must match the cited page of the source PDF (docs/03-data.md section 2).

Proves the number is on the cited page, on the row of the analyte, in the right column position. It does not
replace a human spot-check against the rendered PDF.
"""
import csv
import hashlib
import re
import shutil
import subprocess
from functools import cache

import pytest
import yaml

from contaminated_land.paths import CRITERIA_DIR, SOURCES_YAML, pdf_path

pytestmark = pytest.mark.pdf

SETS = [p for p in sorted(CRITERIA_DIR.glob("*.csv")) if p.stem != "aliases"]
# Analyte -> text that labels its row in the PDF layout (the printed name wraps onto two lines).
ROW_LABEL = {
    "Mercury (inorganic)": "(inorganic)",
    "Carcinogenic PAHs (as BaP TEQ)": "(as BaP TEQ)",
    "Chromium (VI)": "Chromium (VI)",
    "F1": "F1(9)",
    "F2": "F2(10)",
}
# Column order as printed. HIL: A B C D. HSL: four HSL A&B bands first.
HIL_COL = {"HIL A": 0, "HIL D": 3}
HSL_BAND = {"0 m to <1 m": 0, "1 m to <2 m": 1, "2 m to <4 m": 2, "4 m+": 3}


def _rows():
    for p in SETS:
        with open(p, newline="") as f:
            for r in csv.DictReader(f):
                yield pytest.param(p.stem, r, id=f"{p.stem}:{r['analyte']}:{r['depth_band'] or '-'}")


@cache
def _page(doc_id: str, page: int) -> str:
    out = subprocess.run(["pdftotext", "-layout", "-f", str(page), "-l", str(page), str(pdf_path(doc_id)), "-"],
                         capture_output=True, text=True, check=True)
    return out.stdout


@pytest.fixture(scope="module", autouse=True)
def _need_pdf():
    if not shutil.which("pdftotext"):
        pytest.skip("pdftotext not installed")
    if not pdf_path("nepm-asc-b1").is_file():
        pytest.skip("source PDF not fetched (run ingest/fetch_sources.py)")


def test_pdf_sha256_matches_sources_yaml():
    want = next(d["sha256"] for d in yaml.safe_load(open(SOURCES_YAML)) if d["id"] == "nepm-asc-b1")
    assert hashlib.sha256(pdf_path("nepm-asc-b1").read_bytes()).hexdigest() == want


@pytest.mark.parametrize("set_id,row", list(_rows()))
def test_row_matches_pdf(set_id, row):
    text = _page(row["source_doc_id"], int(row["page"]))
    assert re.sub(r"\s+", " ", row["table_ref"]) in re.sub(r"\s+", " ", text)
    label = ROW_LABEL.get(row["analyte"], row["analyte"])

    if row["soil_type"]:  # HSL: only the rows between the SAND and SILT headings
        text = text.split("SAND", 1)[1].split("SILT", 1)[0]
        col, width = HSL_BAND[row["depth_band"]], 13
    else:
        col, width = HIL_COL[row["land_use"]], 4

    for line in text.splitlines():
        cells = re.split(r"\s{2,}", line.strip())
        if re.fullmatch(re.escape(label) + r"\d{0,2}", cells[0]) and len(cells) == width + 1:
            printed = cells[1 + col].replace(" ", "")  # "3 000" is printed with a thousands space
            assert printed == (row["criterion"] or "NL"), f"{line.strip()!r}"
            return
    pytest.fail(f"no row for {row['analyte']!r} with {width} value cells on page {row['page']}")
