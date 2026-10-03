"""Filesystem layout. Every module resolves paths through here, never by hand."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
SOURCES_YAML = DATA / "sources.yaml"
CRITERIA_DIR = DATA / "criteria"
LAB_DIR = DATA / "lab"
SITES_YAML = LAB_DIR / "sites.yaml"
CACHE = DATA / "cache"
PDF_DIR = CACHE / "pdf"          # downloaded source PDFs, <doc_id>.pdf
DOCLING_DIR = CACHE / "docling"  # parsed docling JSON, <doc_id>.json
LANCEDB_DIR = CACHE / "lancedb"  # LanceDB database (table "chunks")


def pdf_path(doc_id: str) -> Path:
    return PDF_DIR / f"{doc_id}.pdf"
