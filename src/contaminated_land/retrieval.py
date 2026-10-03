"""Search over the LanceDB "chunks" table built by ingest/build_index.py. No LLM call."""
import lancedb
from fastembed import TextEmbedding
from lancedb.rerankers import RRFReranker

from contaminated_land.paths import LANCEDB_DIR
from contaminated_land.types import Passage, SearchMode

EMBED_MODEL = "BAAI/bge-small-en-v1.5"  # must match ingest/build_index.py
_COLS = ["chunk_id", "doc_id", "doc_title", "page", "section", "text"]
_POOL = 30  # candidates fetched per leg before truncating to top_k, so RRF fuses a deep pool
_state: dict = {}  # lazily opened table + embedder, once per process


def _open():
    if "table" not in _state:
        try:
            _state["table"] = lancedb.connect(str(LANCEDB_DIR)).open_table("chunks")
        except Exception as e:  # lancedb raises ValueError/FileNotFoundError depending on what is missing
            raise RuntimeError(f"search index missing at {LANCEDB_DIR}: run ingest/build_index.py") from e
        _state["embedder"] = TextEmbedding(EMBED_MODEL)
    return _state["table"], _state["embedder"]


def covers_page(page: int, page_end: int, target: int) -> bool:
    """A chunk is labelled with its first page but can run onto later ones; true if target is within the span."""
    return page <= target <= page_end


def page_ends(chunk_ids: list[str]) -> dict[str, int]:
    """Last page of each chunk (the Passage contract carries only the first). For evals, not the MCP tools."""
    if not chunk_ids:
        return {}
    table, _ = _open()
    rows = table.search().where("chunk_id IN (" + ", ".join(f"'{c}'" for c in chunk_ids) + ")").select(
        ["chunk_id", "page_end"]
    ).limit(len(chunk_ids)).to_list()
    return {r["chunk_id"]: r["page_end"] for r in rows}


def search(query: str, top_k: int = 5, doc_ids: list[str] | None = None, mode: SearchMode = "hybrid") -> list[Passage]:
    """Rank chunks from the LanceDB index. top_k is clamped to 1..20. No LLM call."""
    top_k = max(1, min(20, top_k))
    if doc_ids == []:
        return []
    table, embedder = _open()
    if mode == "bm25":
        q, score = table.search(query, query_type="fts"), "_score"
    else:
        vec = next(iter(embedder.query_embed(query)))
        if mode == "vector":
            q, score = table.search(vec).distance_type("cosine"), "_distance"
        else:  # hybrid: vector + native FTS fused with reciprocal rank fusion
            q = table.search(query_type="hybrid").vector(vec).text(query).rerank(RRFReranker())
            score = "_relevance_score"
    if doc_ids is not None:
        q = q.where("doc_id IN (" + ", ".join("'" + d.replace("'", "''") + "'" for d in doc_ids) + ")")
    rows = q.select(_COLS).limit(_POOL).to_list()[:top_k]
    return [
        Passage(**{k: r[k] for k in _COLS}, score=float(1 - r[score] if score == "_distance" else r[score]))
        for r in rows
    ]
