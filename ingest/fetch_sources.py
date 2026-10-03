"""Download every PDF in data/sources.yaml to data/cache/pdf/ and record sha256, retrieved, pages.

Fails loudly if a document already has a recorded sha256 and the download differs.
Usage: uv run python ingest/fetch_sources.py
"""
import datetime
import hashlib
import urllib.request

import yaml
from pypdf import PdfReader

from site_assess.paths import PDF_DIR, SOURCES_YAML, pdf_path

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        body = r.read()
    if not body.startswith(b"%PDF"):
        raise RuntimeError(f"not a PDF: {url}")
    return body


def main() -> None:
    sources = yaml.safe_load(SOURCES_YAML.read_text())
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    for doc in sources:
        path = pdf_path(doc["id"])
        body = path.read_bytes() if path.exists() else fetch(doc["url"])
        digest = hashlib.sha256(body).hexdigest()
        if doc.get("sha256") and doc["sha256"] != digest:
            raise RuntimeError(f"{doc['id']}: sha256 changed; re-run the criteria transcription check")
        path.write_bytes(body)
        doc["sha256"] = digest
        doc.setdefault("retrieved", datetime.date.today())
        doc["pages"] = len(PdfReader(path).pages)
        print(f"{doc['id']}: {doc['pages']} pages, {len(body)} bytes, sha256 {digest[:12]}")
    header = "".join(line + "\n" for line in SOURCES_YAML.read_text().splitlines() if line.startswith("#"))
    SOURCES_YAML.write_text(header + yaml.safe_dump(sources, sort_keys=False, allow_unicode=True))


if __name__ == "__main__":
    main()
