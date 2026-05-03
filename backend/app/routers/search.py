"""
Arama Router — GET /ara
Hibrit: BM25 (MySQL FULLTEXT) + Semantik (Qdrant) → RRF Fusion
Qdrant hazır değilse otomatik BM25-only fallback
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.database.schemas import SearchResponse
from app.services.bm25_service import detect_language
from app.services.hybrid_service import hybrid_search

router = APIRouter(tags=["arama"])

DbDep = Annotated[AsyncSession, Depends(get_db)]


@router.get("/ara", response_model=SearchResponse)
async def ara(
    db: DbDep,
    q: str   = Query(..., min_length=1, max_length=500, description="Arama sorgusu"),
    dil: str = Query("auto", description="'ar', 'en' veya 'auto'"),
    sayfa: int = Query(1, ge=1, description="Sayfa numarası"),
    limit: int = Query(10, ge=1, le=50, description="Sayfa başına sonuç"),
    mod: str = Query("hybrid", description="Arama modu: 'hybrid', 'bm25', 'vector'"),
):
    gercek_dil = dil if dil in ("ar", "en") else detect_language(q)

    sonuclar, toplam, donen_mod = await hybrid_search(
        db, q, dil=dil, sayfa=sayfa, limit=limit, search_mode=mod
    )

    return SearchResponse(
        sorgu=q,
        dil=gercek_dil,
        mod=donen_mod,
        sayfa=sayfa,
        toplam=toplam,
        sonuclar=sonuclar,  # type: ignore[arg-type]
    )
