"""
Qdrant Vektör Arama Servisi
============================
Semantic search: sorgu → embedding → Qdrant nearest neighbors
"""

from functools import lru_cache
from typing import TYPE_CHECKING

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, SearchRequest

from app.config import settings

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer


# ── Singleton: Model ve Client (uygulama boyu bir kez yüklenir) ──────────────

@lru_cache(maxsize=1)
def get_embedding_model() -> "SentenceTransformer":
    """Sentence transformer modelini yükle (ilk çağrıda indirir)."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(settings.embedding_model)


@lru_cache(maxsize=1)
def get_qdrant_client() -> QdrantClient:
    return QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)


# ── Encoding ─────────────────────────────────────────────────────────────────

def _encode_query_sync(text: str) -> list[float]:
    """Sorgu metnini vektöre dönüştür."""
    model = get_embedding_model()
    vector = model.encode(
        text,
        normalize_embeddings=True,   # cosine similarity için
        show_progress_bar=False,
    )
    return vector.tolist()


# ── Arama ────────────────────────────────────────────────────────────────────

def _qdrant_search_sync(collection: str, query_vector: list[float], top_k: int):
    client = get_qdrant_client()
    res = client.query_points(
        collection_name=collection,
        query=query_vector,
        limit=top_k,
        with_payload=True,
        score_threshold=0.0,
    )
    return res.points

async def vector_search(
    query: str,
    lang: str = "en",
    top_k: int = 50,
) -> list[dict]:
    """
    Qdrant'ta semantic arama yapar.
    Döner: [{"hadis_id": int, "score": float}, ...]
    top_k: RRF fusion için geniş tutuluyor (varsayılan 50)
    """
    import asyncio
    
    collection = (
        settings.qdrant_collection_ar if lang == "ar"
        else settings.qdrant_collection_en
    )
    
    # Embedding işlemini ayrı thread'de yap
    query_vector = await asyncio.to_thread(_encode_query_sync, query)

    # Qdrant aramasını ayrı thread'de yap
    results = await asyncio.to_thread(_qdrant_search_sync, collection, query_vector, top_k)

    return [
        {
            "hadis_id": int(hit.id),
            "score":    float(hit.score),
        }
        for hit in results
    ]


async def is_qdrant_ready(lang: str = "en") -> bool:
    """Qdrant collection'ı hazır mı? (embedding'ler yüklenmiş mi?)"""
    try:
        col = (
            settings.qdrant_collection_ar if lang == "ar"
            else settings.qdrant_collection_en
        )
        client = get_qdrant_client()
        info = client.get_collection(col)
        return (info.points_count or 0) > 0
    except Exception:
        return False
