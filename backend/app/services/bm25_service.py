"""
BM25 benzeri arama — MySQL FULLTEXT (NATURAL LANGUAGE MODE)
"""

import re

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


ARABIC_RE = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+")
ARABIC_DIACRITICS_RE = re.compile(
    r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC"
    r"\u06DF-\u06E4\u06E7\u06E8\u06EA-\u06ED]"
)
ARABIC_NON_TEXT_RE = re.compile(r"[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\s]+")

ARABIC_TOPIC_VARIANTS = {
    "\u0635\u064a\u0627\u0645": [
        "\u0635\u0648\u0645",
        "\u0635\u0627\u0626\u0645",
    ],
    "\u0635\u0648\u0645": [
        "\u0635\u064a\u0627\u0645",
        "\u0635\u0627\u0626\u0645",
    ],
    "\u0635\u0628\u0631": [
        "\u0635\u0627\u0628\u0631",
    ],
    "\u0635\u062f\u0642\u0647": [
        "\u062a\u0635\u062f\u0642",
        "\u0635\u062f\u0642\u0627\u062a",
    ],
}


def detect_language(query: str) -> str:
    """Sorguda Arapça karakter varsa 'ar', yoksa 'en' döner."""
    return "ar" if ARABIC_RE.search(query) else "en"


def normalize_arabic_query(query: str) -> str:
    text_value = ARABIC_DIACRITICS_RE.sub("", query or "")
    text_value = re.sub(r"[\u0625\u0623\u0622\u0671]", "\u0627", text_value)
    text_value = text_value.replace("\u0629", "\u0647")
    text_value = ARABIC_NON_TEXT_RE.sub(" ", text_value)
    return re.sub(r"\s+", " ", text_value).strip()


def build_arabic_terms(query: str) -> list[tuple[str, int]]:
    normalized = normalize_arabic_query(query)
    weighted_terms: list[tuple[str, int]] = []

    def add(term: str, weight: int) -> None:
        if len(term) < 3:
            return
        if not any(existing == term for existing, _ in weighted_terms):
            weighted_terms.append((term, weight))

    for token in normalized.split():
        add(token, 30)

        if token.startswith("\u0627\u0644") and len(token) > 4:
            token_without_article = token[2:]
            add(token_without_article, 24)
        else:
            token_without_article = token

        for variant in ARABIC_TOPIC_VARIANTS.get(token_without_article, []):
            add(variant, 14)

    return weighted_terms


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
        arabic_query = normalize_arabic_query(query)
        arabic_terms = build_arabic_terms(query)
        params = {"q": arabic_query, "limit": limit, "offset": offset}
        where_parts = []
        score_parts = []

        if arabic_query:
            params["phrase"] = f"%{arabic_query}%"
            score_parts.append("CASE WHEN ha.metin_temiz LIKE :phrase THEN 60 ELSE 0 END")

        for idx, (term, weight) in enumerate(arabic_terms):
            param_name = f"term_{idx}"
            params[param_name] = f"%{term}%"
            where_parts.append(f"ha.metin_temiz LIKE :{param_name}")
            score_parts.append(
                f"CASE WHEN ha.metin_temiz LIKE :{param_name} THEN {weight} ELSE 0 END"
            )

        where_sql = " OR ".join(where_parts) if where_parts else "0 = 1"
        score_sql = " + ".join(score_parts) if score_parts else "0"
        score_sql = (
            f"({score_sql} + "
            "MATCH(ha.metin_temiz) AGAINST(:q IN NATURAL LANGUAGE MODE) * 0.05)"
        )

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
                hi.hadith_detail AS en_detail,
                {score_sql} AS skor
            FROM hadisler h
            JOIN hadis_arapca ha ON ha.hadis_id = h.id
            LEFT JOIN hadis_ingilizce hi ON hi.hadis_id = h.id
            WHERE {where_sql}
            ORDER BY skor DESC, h.id ASC
            LIMIT :limit OFFSET :offset
        """)
        count_sql = text(f"""
            SELECT COUNT(*) FROM hadis_arapca
            WHERE {where_sql.replace("ha.", "")}
        """)
    else:
        # İngilizce FULLTEXT
        params = {"q": query, "limit": limit, "offset": offset}
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

    result = await db.execute(sql, params)
    c_result = await db.execute(count_sql, params)

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
