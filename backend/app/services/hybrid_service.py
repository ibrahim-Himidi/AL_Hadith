"""
Hibrit Arama Servisi — BM25 + Semantik → RRF Fusion
=====================================================
Reciprocal Rank Fusion (RRF):
    RRF_score(d) = Σ 1 / (k + rank_i(d))
    k = 60 (standart değer, outlier'ları bastırır)

Sonuçlar MySQL'den tam metin ile zenginleştirilir.
"""

import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.bm25_service import bm25_search, detect_language
from app.services.vector_service import is_qdrant_ready, vector_search

RRF_K = 60  # Standart RRF parametresi


# ─────────────────────────────────────────────────────────────────────────────
# RRF Fusion
# ─────────────────────────────────────────────────────────────────────────────

def reciprocal_rank_fusion(
    bm25_results: list[dict],
    vector_results: list[dict],
    bm25_weight: float = 0.4,
    vector_weight: float = 0.6,
) -> list[dict]:
    """
    BM25 ve semantik sonuçlarını RRF ile birleştirir.
    
    bm25_results   : [{"id": int, ...}, ...]
    vector_results : [{"hadis_id": int, "score": float}, ...]
    Döner          : [{"hadis_id": int, "rrf_score": float}] azalan sırada
    """
    scores: dict[int, float] = {}

    # BM25 skorları
    for rank, item in enumerate(bm25_results, start=1):
        hid = item["id"]
        scores[hid] = scores.get(hid, 0.0) + bm25_weight * (1.0 / (RRF_K + rank))

    # Semantik skorlar
    for rank, item in enumerate(vector_results, start=1):
        hid = item["hadis_id"]
        scores[hid] = scores.get(hid, 0.0) + vector_weight * (1.0 / (RRF_K + rank))

    # Azalan sırada sırala
    fused = [
        {"hadis_id": hid, "rrf_score": score}
        for hid, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)
    ]
    return fused


# ─────────────────────────────────────────────────────────────────────────────
# Hadis verilerini MySQL'den çek
# ─────────────────────────────────────────────────────────────────────────────

async def fetch_hadis_details(db: AsyncSession, hadis_ids: list[int]) -> dict[int, dict]:
    """Verilen ID listesi için hadis detaylarını MySQL'den çek."""
    if not hadis_ids:
        return {}

    placeholders = ", ".join(str(i) for i in hadis_ids)
    sql = text(f"""
        SELECT
            h.id,
            h.hadis_no,
            h.kitap,
            h.bab,
            h.ravi,
            h.kaynak_link,
            ha.sanad        AS ar_sanad,
            ha.hadith_detail AS ar_detail,
            hi.sanad        AS en_sanad,
            hi.hadith_detail AS en_detail
        FROM hadisler h
        LEFT JOIN hadis_arapca ha ON ha.hadis_id = h.id
        LEFT JOIN hadis_ingilizce hi ON hi.hadis_id = h.id
        WHERE h.id IN ({placeholders})
    """)

    result = await db.execute(sql)
    rows = result.mappings().all()

    return {
        row["id"]: {
            "id":          row["id"],
            "hadis_no":    row["hadis_no"],
            "kitap":       row["kitap"],
            "bab":         row["bab"],
            "ravi":        row["ravi"],
            "kaynak_link": row["kaynak_link"],
            "arapca": {
                "sanad":         row["ar_sanad"],
                "hadith_detail": row["ar_detail"],
            } if row["ar_detail"] else None,
            "ingilizce": {
                "sanad":         row["en_sanad"],
                "hadith_detail": row["en_detail"],
            } if row["en_detail"] else None,
        }
        for row in rows
    }


# ─────────────────────────────────────────────────────────────────────────────
# Ana hibrit arama fonksiyonu
# ─────────────────────────────────────────────────────────────────────────────

async def hybrid_search(
    db: AsyncSession,
    query: str,
    dil: str = "auto",
    sayfa: int = 1,
    limit: int = 10,
    search_mode: str = "hybrid",
) -> tuple[list[dict], int, str]:
    """
    Hibrit arama: BM25 + Semantik → RRF Fusion.
    
    Eğer Qdrant hazır değilse (embedding'ler yüklenmemişse)
    sadece BM25 sonuçlarını döner.
    
    Döner: (sonuçlar, toplam, mod)
    mod: "hybrid" | "bm25_only"
    """
    # Dil tespiti
    if dil == "auto":
        dil = detect_language(query)

    # Qdrant hazır mı kontrol et
    qdrant_ok = await is_qdrant_ready(dil)

    if not qdrant_ok or search_mode == "bm25":
        # Sadece BM25
        sonuclar, toplam = await bm25_search(db, query, dil=dil, sayfa=sayfa, limit=limit)
        return sonuclar, toplam, "bm25_only"

    if search_mode == "vector":
        # Sadece Vektör Arama
        vector_raw = await vector_search(query, lang=dil, top_k=limit * sayfa)
        toplam = len(vector_raw)
        offset = (sayfa - 1) * limit
        page_ids = [item["hadis_id"] for item in vector_raw[offset : offset + limit]]
        score_map = {item["hadis_id"]: item["score"] for item in vector_raw}

        if not page_ids:
            return [], toplam, "vector_only"
            
        details = await fetch_hadis_details(db, page_ids)
        sonuclar = []
        for hid in page_ids:
            if hid in details:
                item = details[hid].copy()
                item["skor"] = round(score_map[hid], 6)
                sonuclar.append(item)
        return sonuclar, toplam, "vector_only"

    # ── Paralel: BM25 + Semantik arama aynı anda ──────────────────────────
    TOP_K = 100  # her kaynaktan en fazla 100 sonuç al, sonra RRF ile birleştir

    bm25_task   = bm25_search(db, query, dil=dil, sayfa=1, limit=TOP_K)
    vector_task = vector_search(query, lang=dil, top_k=TOP_K)

    (bm25_raw, bm25_total), vector_raw = await asyncio.gather(bm25_task, vector_task)

    # ── RRF Fusion ────────────────────────────────────────────────────────
    fused = reciprocal_rank_fusion(bm25_raw, vector_raw)

    # ── Sayfalama ─────────────────────────────────────────────────────────
    toplam = len(fused)
    offset = (sayfa - 1) * limit
    page_ids = [item["hadis_id"] for item in fused[offset : offset + limit]]
    score_map = {item["hadis_id"]: item["rrf_score"] for item in fused}

    if not page_ids:
        return [], toplam, "hybrid"

    # ── MySQL'den detay çek ───────────────────────────────────────────────
    details = await fetch_hadis_details(db, page_ids)

    # ── Sırayı koru + skor ekle ────────────────────────────────────────────
    sonuclar = []
    for hid in page_ids:
        if hid in details:
            item = details[hid].copy()
            item["skor"] = round(score_map[hid], 6)
            sonuclar.append(item)

    return sonuclar, toplam, "hybrid"
