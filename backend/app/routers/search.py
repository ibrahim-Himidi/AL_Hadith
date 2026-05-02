"""
Arama Router — GET /ara
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.database.schemas import SearchResponse
from app.services.bm25_service import bm25_search, detect_language

router = APIRouter(tags=["arama"])

DbDep = Annotated[AsyncSession, Depends(get_db)]


@router.get("/ara", response_model=SearchResponse)
async def ara(
    db: DbDep,
    q: str = Query(..., min_length=1, max_length=500, description="Arama sorgusu"),
    dil: str = Query("auto", description="'ar', 'en' veya 'auto'"),
    sayfa: int = Query(1, ge=1, description="Sayfa numarası"),
    limit: int = Query(10, ge=1, le=50, description="Sayfa başına sonuç"),
):
    # Faz 1: sadece BM25 (MySQL FULLTEXT)
    # Faz 2'de semantic + RRF eklenecek
    gercek_dil = dil if dil in ("ar", "en") else detect_language(q)

    sonuclar, toplam = await bm25_search(db, q, dil=dil, sayfa=sayfa, limit=limit)

    return SearchResponse(
        sorgu=q,
        dil=gercek_dil,
        sayfa=sayfa,
        toplam=toplam,
        sonuclar=sonuclar,  # type: ignore[arg-type]
    )
