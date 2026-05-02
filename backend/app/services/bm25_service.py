"""
BM25 benzeri arama — MySQL FULLTEXT (NATURAL LANGUAGE MODE)
"""

import re

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import Hadis, HadisArapca, HadisIngilizce


def detect_language(query: str) -> str:
    """Sorguda Arapça karakter varsa 'ar', yoksa 'en' döner."""
    arabic_range = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+')
    return "ar" if arabic_range.search(query) else "en"


async def bm25_search(
    db: AsyncSession,
    query: str,
    dil: str = "auto",
    sayfa: int = 1,
    limit: int = 10,
) -> tuple[list[dict], int]:
    """
    MySQL FULLTEXT ile arama.
    Döner: (sonuçlar, toplam_sayı)
    Her sonuç: {hadis_id, skor, ...}
    """
    if dil == "auto":
        dil = detect_language(query)

    offset = (sayfa - 1) * limit

    if dil == "ar":
        # Arapça FULLTEXT (ngram parser)
        sql = text("""
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
                hi.hadith_detail AS en_detail,
                MATCH(ha.metin_temiz) AGAINST(:q IN NATURAL LANGUAGE MODE) AS skor
            FROM hadisler h
            JOIN hadis_arapca ha ON ha.hadis_id = h.id
            LEFT JOIN hadis_ingilizce hi ON hi.hadis_id = h.id
            WHERE MATCH(ha.metin_temiz) AGAINST(:q IN NATURAL LANGUAGE MODE) > 0
            ORDER BY skor DESC
            LIMIT :limit OFFSET :offset
        """)
        count_sql = text("""
            SELECT COUNT(*) FROM hadis_arapca
            WHERE MATCH(metin_temiz) AGAINST(:q IN NATURAL LANGUAGE MODE) > 0
        """)
    else:
        # İngilizce FULLTEXT
        sql = text("""
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
                hi.hadith_detail AS en_detail,
                MATCH(hi.metin_temiz) AGAINST(:q IN NATURAL LANGUAGE MODE) AS skor
            FROM hadisler h
            JOIN hadis_ingilizce hi ON hi.hadis_id = h.id
            LEFT JOIN hadis_arapca ha ON ha.hadis_id = h.id
            WHERE MATCH(hi.metin_temiz) AGAINST(:q IN NATURAL LANGUAGE MODE) > 0
            ORDER BY skor DESC
            LIMIT :limit OFFSET :offset
        """)
        count_sql = text("""
            SELECT COUNT(*) FROM hadis_ingilizce
            WHERE MATCH(metin_temiz) AGAINST(:q IN NATURAL LANGUAGE MODE) > 0
        """)

    result  = await db.execute(sql,       {"q": query, "limit": limit, "offset": offset})
    c_result = await db.execute(count_sql, {"q": query})

    rows  = result.mappings().all()
    total = c_result.scalar_one_or_none() or 0

    sonuclar = []
    for row in rows:
        sonuclar.append({
            "id":          row["id"],
            "hadis_no":    row["hadis_no"],
            "kitap":       row["kitap"],
            "bab":         row["bab"],
            "ravi":        row["ravi"],
            "kaynak_link": row["kaynak_link"],
            "arapca":      {"sanad": row["ar_sanad"], "hadith_detail": row["ar_detail"]} if row["ar_detail"] else None,
            "ingilizce":   {"sanad": row["en_sanad"], "hadith_detail": row["en_detail"]} if row["en_detail"] else None,
            "skor":        float(row["skor"]) if row["skor"] else 0.0,
        })

    return sonuclar, int(total)
