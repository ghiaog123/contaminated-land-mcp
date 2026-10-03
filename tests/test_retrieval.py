"""Smoke tests for search over the built index. Run ingest/build_index.py first."""
import importlib.util
import re
from pathlib import Path

import pytest
import yaml

from contaminated_land.paths import SOURCES_YAML
from contaminated_land.retrieval import covers_page, page_ends, search

PAGES = {d["id"]: d["pages"] for d in yaml.safe_load(SOURCES_YAML.read_text())}
CHUNK_ID = re.compile(r"^(?P<doc>[a-z0-9-]+):p(?P<page>\d+):\d{4}$")


index = pytest.mark.index


@index
def test_hybrid_returns_valid_b1_passages():
    res = search("health investigation levels residential", top_k=5)
    assert res and any(p["doc_id"] == "nepm-asc-b1" for p in res)
    for p in res:
        m = CHUNK_ID.match(p["chunk_id"])
        assert m and m["doc"] == p["doc_id"] and int(m["page"]) == p["page"]
        assert 1 <= p["page"] <= PAGES[p["doc_id"]]
        assert p["text"] and p["doc_title"]
    ends = page_ends([p["chunk_id"] for p in res])
    assert all(ends[p["chunk_id"]] >= p["page"] for p in res)


@index
def test_bm25_exact_term():
    res = search("benzene", mode="bm25")
    assert res and all("benzene" in p["text"].lower() for p in res)


@index
@pytest.mark.parametrize("mode", ["bm25", "vector", "hybrid"])
def test_doc_ids_filter(mode):
    res = search("site characterisation sampling", top_k=10, doc_ids=["nepm-asc-b2"], mode=mode)
    assert res and {p["doc_id"] for p in res} == {"nepm-asc-b2"}
    assert search("sampling", doc_ids=[]) == []


@index
def test_top_k_clamped():
    assert len(search("soil", top_k=0)) == 1
    assert len(search("soil", top_k=500, mode="vector")) == 20


@index
def test_fts_special_characters_do_not_crash():
    assert search("Table 1A(1) HIL A: 'lead' AND/OR (arsenic)", mode="bm25") is not None


def test_covers_page_span():
    assert covers_page(72, 73, 73) and covers_page(72, 73, 72)
    assert not covers_page(72, 73, 74) and not covers_page(73, 73, 72)


def test_separator_only_chunks_are_dropped():
    path = Path(__file__).parents[1] / "ingest" / "build_index.py"
    spec = importlib.util.spec_from_file_location("build_index", path)
    build_index = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build_index)
    assert build_index.is_separator_only("|---|:--:|\n| - | |") and build_index.is_separator_only("  ")
    assert not build_index.is_separator_only("| a | b |\n|---|---|")
    assert build_index.NOTES_HEADING.match("Notes:") and not build_index.NOTES_HEADING.match("Notes on soil")
