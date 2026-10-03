"""Deterministic screening of lab results against a criteria table. No LLM, ever (D6).

Rules (docs/03-data.md "Screening semantics"): exceedance iff result > criterion strictly, after an explicit
unit conversion; `<` results are never compared; anything that cannot be compared lands in `not_screened`
with a reason. All comparisons use Decimal so 3000 ug/kg vs 3 mg/kg is exactly equal, not 3.0000000000000004.
"""
import csv
import re
from decimal import ROUND_HALF_UP, Decimal
from functools import cache, lru_cache

import yaml

from site_assess.paths import CRITERIA_DIR, LAB_DIR, SITES_YAML, SOURCES_YAML
from site_assess.types import CriteriaSetInfo, Exceedance, NotScreened, ScreeningResult

# The only conversions the code performs: (lab unit, criterion unit) -> multiplier. Anything else is unit_mismatch.
_UNIT_FACTORS = {
    ("mg/kg", "mg/kg"): Decimal(1),
    ("ug/kg", "ug/kg"): Decimal(1),
    ("ug/kg", "mg/kg"): Decimal("0.001"),
    ("mg/kg", "ug/kg"): Decimal(1000),
}

NOTES = [
    "Exceedance means result strictly greater than the criterion after unit conversion; a result equal to the "
    "criterion is not an exceedance.",
    "Results qualified '<' (below the limit of reporting) are not compared, even when the limit of reporting "
    "is above the criterion.",
    "Duplicate samples are screened independently as separate samples; no averaging and no worst-case "
    "selection is applied.",
    "samples_screened and analytes_screened count only results compared against a numeric criterion.",
    "Depth bands are lower-bound inclusive and upper-bound exclusive (a sample at exactly 1.0 m falls in "
    "'1 m to <2 m').",
]


def _read_csv(path) -> list[dict]:
    """CSV rows, skipping '# ...' comment lines (the synthetic-data header)."""
    with open(path, newline="") as f:
        return list(csv.DictReader(line for line in f if not line.startswith("#")))


@lru_cache(maxsize=1)
def _aliases() -> dict[str, str]:
    return {r["lab_spelling"].strip().lower(): r["canonical"] for r in _read_csv(CRITERIA_DIR / "aliases.csv")}


@cache
def _load_criteria(criteria_set: str) -> list[dict]:
    path = CRITERIA_DIR / f"{criteria_set}.csv"
    if criteria_set == "aliases" or not path.is_file():
        raise ValueError(f"unknown criteria_set {criteria_set!r}; known: {[c['id'] for c in list_criteria_sets()]}")
    rows = _read_csv(path)
    for r in rows:
        if not (r["source_doc_id"] and r["page"] and r["table_ref"]):
            raise ValueError(f"{path.name}: row for {r['analyte']!r} lacks source_doc_id, page or table_ref")
    return rows


@lru_cache(maxsize=1)
def _doc_titles() -> dict[str, str]:
    with open(SOURCES_YAML) as f:
        return {d["id"]: d["title"] for d in yaml.safe_load(f)}


def list_criteria_sets() -> list[CriteriaSetInfo]:
    out = []
    for path in sorted(CRITERIA_DIR.glob("*.csv")):
        if path.stem == "aliases":
            continue
        r = _read_csv(path)[0]
        out.append({
            "id": path.stem,
            "title": f"{_doc_titles().get(r['source_doc_id'], r['source_doc_id'])}, {r['table_ref']}, "
                     f"{r['land_use']} ({r['matrix']})",
            "source": {"doc_id": r["source_doc_id"], "page": int(r["page"]), "table": r["table_ref"]},
            "land_use": r["land_use"],
            "matrix": r["matrix"],
        })
    return out


def load_sites() -> list[dict]:
    """Rows of data/lab/sites.yaml (site_id, client_name, site_address, land_use, soil_type, story)."""
    with open(SITES_YAML) as f:
        return yaml.safe_load(f)


def _letters(text: str) -> set[str]:
    """Scenario letters in a label: 'HIL A' -> {a}, 'HSL A & HSL B' -> {a, b}, 'residential-a' -> {a}."""
    return {m.lower() for m in re.findall(r"(?<![A-Za-z])[A-Da-d](?![A-Za-z])", text)}


def _band_contains(band: str, depth: Decimal) -> bool:
    """Band labels as printed in Table 1A(3): '0 m to <1 m', '4 m+'.

    Boundary convention: lower bound inclusive, upper bound exclusive. The table prints '<1 m' as the upper
    limit of the first band and '1 m to' as the start of the next, so a sample at exactly 1.0 m is in the
    '1 m to <2 m' band. '4 m+' starts at 4.0 m inclusive.
    """
    m = re.fullmatch(r"([\d.]+) m to <([\d.]+) m", band)
    if m:
        return Decimal(m[1]) <= depth < Decimal(m[2])
    m = re.fullmatch(r"([\d.]+) m\+", band)
    if m:
        return depth >= Decimal(m[1])
    raise ValueError(f"unparseable depth_band {band!r}")


def _quantize2(x: Decimal) -> float:
    return float(x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def screen(site_id: str, criteria_set: str) -> ScreeningResult:
    """Deterministic: same input, same output. Raises ValueError for unknown ids or a set that contradicts the site."""
    site = next((s for s in load_sites() if s["site_id"] == site_id), None)
    if site is None:
        raise ValueError(f"unknown site_id {site_id!r}; known: {[s['site_id'] for s in load_sites()]}")
    criteria = _load_criteria(criteria_set)

    # Scenario family check: the set's letters (A/B/C/D) must overlap the site's land use (plus any
    # `also_screen_as` scenarios the site declares), and an HSL set's soil type must be the site's.
    set_letters = _letters(criteria[0]["land_use"])
    site_letters = _letters(site["land_use"]).union(*(_letters(x) for x in site.get("also_screen_as", [])))
    if not set_letters & site_letters:
        raise ValueError(f"criteria_set {criteria_set!r} ({criteria[0]['land_use']}) contradicts site land_use "
                         f"{site['land_use']!r}")
    set_soils = {r["soil_type"] for r in criteria if r["soil_type"]}
    if set_soils and site.get("soil_type") not in set_soils:
        raise ValueError(f"criteria_set {criteria_set!r} is for soil {sorted(set_soils)}, "
                         f"site is {site.get('soil_type')!r}")

    by_analyte: dict[tuple[str, str], list[dict]] = {}
    for r in criteria:
        by_analyte.setdefault((r["analyte"].lower(), r["matrix"]), []).append(r)

    exceedances: list[Exceedance] = []
    not_screened: list[NotScreened] = []
    compared_samples: set[str] = set()
    compared_analytes: set[str] = set()

    for row in _read_csv(LAB_DIR / f"{site_id}.csv"):
        lab_name = row["analyte"].strip()
        name = _aliases().get(lab_name.lower(), lab_name)
        sample, depth_txt = row["sample_id"], row["depth_m"].strip()

        def skip(reason, sample=sample, name=name):
            not_screened.append({"sample_id": sample, "analyte": name, "reason": reason})

        if row["qualifier"].strip() == "<":
            skip("below_lor")
            continue
        cands = by_analyte.get((name.lower(), row["matrix"]))
        if not cands:
            skip("no_criterion")
            continue
        if any(c["depth_band"] for c in cands):
            if not depth_txt:
                skip("no_depth")
                continue
            depth = Decimal(depth_txt)
            cands = [c for c in cands
                     if c["soil_type"] == site.get("soil_type") and _band_contains(c["depth_band"], depth)]
            if not cands:
                skip("no_depth")
                continue
        crit = cands[0]
        if not crit["criterion"].strip():
            skip("non_numeric_criterion")
            continue
        factor = _UNIT_FACTORS.get((row["unit"].strip().lower().replace("µ", "u"), crit["unit"]))
        if factor is None:
            skip("unit_mismatch")
            continue

        result, limit = Decimal(row["result"]) * factor, Decimal(crit["criterion"])
        compared_samples.add(sample)
        compared_analytes.add(crit["analyte"])
        if result > limit:
            exceedances.append({
                "sample_id": sample,
                "depth_m": float(depth_txt) if depth_txt else None,
                "analyte": crit["analyte"],
                "result": float(row["result"]),
                "unit": row["unit"],
                "criterion": float(limit),
                "criterion_unit": crit["unit"],
                "ratio": _quantize2(result / limit),
                "source": {"doc_id": crit["source_doc_id"], "page": int(crit["page"]), "table": crit["table_ref"]},
            })

    exceedances.sort(key=lambda e: (e["sample_id"], e["analyte"]))
    not_screened.sort(key=lambda n: (n["sample_id"], n["analyte"], n["reason"]))
    return {
        "site_id": site_id,
        "criteria_set": criteria_set,
        "samples_screened": len(compared_samples),
        "analytes_screened": len(compared_analytes),
        "exceedances": exceedances,
        "not_screened": not_screened,
        "notes": list(NOTES),
    }
