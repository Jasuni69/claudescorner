"""
shared/embedder.py — reusable semantic embedding utility.
Shared by memory-mcp and skill-manager-mcp (and any future MCP server).
"""
import json
from pathlib import Path

EMBED_MODEL = "all-MiniLM-L6-v2"

_embedder = None
_embed_available = False


def load_embedder() -> bool:
    global _embedder, _embed_available
    if _embed_available:
        return True
    try:
        from sentence_transformers import SentenceTransformer
        _embedder = SentenceTransformer(EMBED_MODEL)
        _embed_available = True
        return True
    except Exception:
        return False


def embed(texts: list[str]):
    """Return numpy array of embeddings, shape (N, D)."""
    if not _embed_available:
        raise RuntimeError("Embedder not loaded — call load_embedder() first")
    return _embedder.encode(texts, convert_to_numpy=True, show_progress_bar=False)


def cosine_scores(query_vec, doc_vecs):
    """Cosine similarity between query_vec (D,) and doc_vecs (N, D). Returns shape (N,)."""
    import numpy as np
    q = query_vec / (np.linalg.norm(query_vec) + 1e-9)
    norms = np.linalg.norm(doc_vecs, axis=1, keepdims=True) + 1e-9
    return (doc_vecs / norms) @ q


def build_index(doc_ids: list[str], texts: list[str]) -> dict:
    """Build a serialisable embed index: {doc_ids, embeddings}."""
    vecs = embed(texts)
    return {"doc_ids": doc_ids, "embeddings": vecs.tolist()}


def search_index(index: dict, query: str, top_k: int = 5) -> list[tuple[str, float]]:
    """Return [(doc_id, score)] sorted descending."""
    import numpy as np
    if not index.get("doc_ids"):
        return []
    doc_ids = index["doc_ids"]
    doc_vecs = np.array(index["embeddings"], dtype="float32")
    q_vec = embed([query])[0]
    scores = cosine_scores(q_vec, doc_vecs)
    ranked = sorted(zip(doc_ids, scores.tolist()), key=lambda x: -x[1])
    return ranked[:top_k]
