"""docling parse -> HybridChunker -> fastembed -> LanceDB table "chunks" (vector + full-text).

Usage: uv run python ingest/build_index.py
Rerunnable: parsed JSON in data/cache/docling/ is reused; the LanceDB table is overwritten.
"""
import re
import time

import lancedb
import pyarrow as pa
import yaml
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.transforms.chunker.hierarchical_chunker import ChunkingDocSerializer
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from docling_core.transforms.serializer.base import BaseSerializerProvider
from docling_core.transforms.serializer.markdown import MarkdownTableSerializer
from docling_core.types.doc import DoclingDocument, TableItem
from fastembed import TextEmbedding
from lancedb.index import FTS
from pypdf import PdfReader

from contaminated_land.paths import DOCLING_DIR, LANCEDB_DIR, SOURCES_YAML, pdf_path

EMBED_MODEL = "BAAI/bge-small-en-v1.5"  # 384-d; the tokenizer below is the model's own
MAX_TOKENS = 450  # < 512 model limit, leaves room for the "<title> > <section> > p.N" header


NOTES_HEADING = re.compile(r"^notes?:?$", re.I)  # table footnotes sit under a literal "Notes:" heading: useless context


def is_separator_only(text: str) -> bool:
    """True for chunks that are empty or only markdown table separator characters."""
    return not text.strip(" |-:\n")


class MarkdownTablesProvider(BaseSerializerProvider):
    """HybridChunker's default serializes tables as 'row, col = value' triplets; we want markdown."""

    def get_serializer(self, doc: DoclingDocument) -> ChunkingDocSerializer:
        return ChunkingDocSerializer(doc=doc, table_serializer=MarkdownTableSerializer())


def parse(doc_id: str) -> DoclingDocument:
    out = DOCLING_DIR / f"{doc_id}.json"
    if out.exists():
        return DoclingDocument.load_from_json(out)
    opts = PdfPipelineOptions(do_ocr=False, do_table_structure=True)  # born-digital PDFs
    conv = DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)})
    doc = conv.convert(pdf_path(doc_id)).document
    DOCLING_DIR.mkdir(parents=True, exist_ok=True)
    doc.save_as_json(out)
    return doc


def table_captions(doc: DoclingDocument) -> dict[str, str]:
    """self_ref -> caption. A caption-less table on the same or next page continues the previous captioned one."""
    caps, last, last_page = {}, "", 0
    for t in doc.tables:
        page = t.prov[0].page_no if t.prov else 0
        cap = t.caption_text(doc)
        if not cap and page - last_page <= 1:
            cap = last
        caps[t.self_ref], last, last_page = cap, cap, page
    return caps


def chunk(doc: DoclingDocument, chunker: HybridChunker, meta: dict) -> list[dict]:
    rows, caps = [], table_captions(doc)
    for n, c in enumerate(chunker.chunk(dl_doc=doc)):
        pages = [p.page_no for it in c.meta.doc_items for p in it.prov]
        if not pages or is_separator_only(c.text):
            continue
        page, page_end = pages[0], max(pages)  # page = first doc item's page (chunk_id); a chunk can span pages
        headings = [h for h in c.meta.headings or [] if not NOTES_HEADING.match(h.strip())]
        section = " > ".join(headings) if headings else None
        header = " > ".join([meta["title"], *([section] if section else []), f"p.{page}"])
        # a wide table is split into pieces; only the first has the caption, so repeat it on each for embedding + FTS
        captions = dict.fromkeys(
            caps[it.self_ref] for it in c.meta.doc_items if isinstance(it, TableItem) and caps[it.self_ref]
        )
        rows.append({
            "chunk_id": f"{meta['id']}:p{page}:{n:04d}",
            "doc_id": meta["id"],
            "doc_title": meta["title"],
            "page": page,
            "page_end": page_end,
            "section": section,
            "text": c.text,
            "ctx_text": "\n".join([header, *captions, c.text]),
        })
    return rows


def main() -> None:
    t0 = time.time()
    sources = yaml.safe_load(SOURCES_YAML.read_text())
    tok = HuggingFaceTokenizer.from_pretrained(EMBED_MODEL, max_tokens=MAX_TOKENS)
    chunker = HybridChunker(tokenizer=tok, serializer_provider=MarkdownTablesProvider())
    rows: list[dict] = []
    for meta in sources:
        t = time.time()
        doc = parse(meta["id"])
        got = chunk(doc, chunker, meta)
        pages = len(PdfReader(pdf_path(meta["id"])).pages)
        assert all(1 <= r["page"] <= r["page_end"] <= pages for r in got), f"{meta['id']}: chunk outside 1..{pages}"
        print(f"{meta['id']}: {len(got)} chunks, {len(doc.tables)} tables, {pages} pages, "
              f"{time.time() - t:.0f}s", flush=True)
        rows += got

    vecs = list(TextEmbedding(EMBED_MODEL).embed([r["ctx_text"] for r in rows], batch_size=32))
    dim = len(vecs[0])
    tbl = pa.Table.from_pylist(rows).append_column(
        "vector", pa.FixedSizeListArray.from_arrays(pa.array([x for v in vecs for x in v], pa.float32()), dim)
    )
    db = lancedb.connect(str(LANCEDB_DIR))
    table = db.create_table("chunks", data=tbl, mode="overwrite")
    table.create_index("ctx_text", config=FTS(with_position=False), replace=True)
    print(f"indexed {len(rows)} chunks ({dim}-d {EMBED_MODEL}) in {time.time() - t0:.0f}s total")


if __name__ == "__main__":
    main()
