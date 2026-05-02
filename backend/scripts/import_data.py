#!/usr/bin/env python3
"""
CSV Temizleme + MySQL Import Scripti
=====================================
Sahih Bukhari Arapça ve İngilizce CSV dosyalarını temizler
ve MySQL veritabanına aktarır.

Kullanım:
    python import_data.py
    python import_data.py --limit 100   # Test için sadece ilk 100 hadis
"""

import argparse
import csv
import logging
import os
import re
import sys
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv
from tqdm import tqdm

# ── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR  = Path(__file__).resolve().parents[2]
DATA_DIR  = BASE_DIR / "veriler csv"

BUKHARI_AR = DATA_DIR / "bukhari_arabic.csv"
BUKHARI_EN = DATA_DIR / "bukhari_english.csv"

# ── Env ──────────────────────────────────────────────────────────────────────
load_dotenv(BASE_DIR / ".env")

DB_CONFIG = {
    "host":     os.getenv("MYSQL_HOST", "localhost"),
    "port":     int(os.getenv("MYSQL_PORT", 3306)),
    "database": os.getenv("MYSQL_DATABASE", "hadis_db"),
    "user":     os.getenv("MYSQL_USER", "hadis_user"),
    "password": os.getenv("MYSQL_PASSWORD", "hadis_pass"),
    "charset":  "utf8mb4",
    "use_unicode": True,
    "collation": "utf8mb4_unicode_ci",
}

SOURCE_TAG_RE = re.compile(
    r"\[\s*/?\s*(?:name|verse|poem)(?:\s+[^\]]*)?\]",
    re.IGNORECASE,
)
UNKNOWN_MARKER_RE = re.compile(r"\[\s*\?+\s*\]")
ARABIC_BRACKET_NOTE_RE = re.compile(r"\[[^\]\u0600-\u06FF]*[A-Za-z?][^\]]*\]")
WHITESPACE_RE = re.compile(r"\s+")


# ─────────────────────────────────────────────────────────────────────────────
# Metin Temizleme
# ─────────────────────────────────────────────────────────────────────────────

def normalize_display_text(text: str, lang: str = "en") -> str:
    """Kaynak markup kalıntılarını temizle, okunabilir metni koru."""
    if not text:
        return ""

    text = fix_line_endings(text)
    text = SOURCE_TAG_RE.sub("", text)
    text = UNKNOWN_MARKER_RE.sub("", text)

    # Arapça metinde kalan İngilizce editör notları ekrana taşınmasın.
    if lang == "ar":
        text = ARABIC_BRACKET_NOTE_RE.sub("", text)

    text = re.sub(r"\s+([،؛؟,.!?:;])", r"\1", text)
    text = re.sub(r"([({\[])\s+", r"\1", text)
    text = re.sub(r"\s+([)}\]])", r"\1", text)
    text = WHITESPACE_RE.sub(" ", text).strip()
    return text


def clean_arabic(text: str) -> str:
    """Arapça metin: harekeleri kaldır, elif normalize et, boşluk temizle."""
    if not text:
        return ""
    # Harekeleri (tashkeel) kaldır
    text = normalize_display_text(text, lang="ar")
    text = re.sub(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E4\u06E7\u06E8\u06EA-\u06ED]', '', text)
    # Elif varyasyonları → ا
    text = re.sub(r'[إأآٱ]', 'ا', text)
    # Te marbuta → he
    text = text.replace('ة', 'ه')
    # Çift boşluk temizle
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def clean_english(text: str) -> str:
    """İngilizce metin: küçük harf, noktalama temizle, boşluk normalize."""
    if not text:
        return ""
    text = normalize_display_text(text, lang="en")
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def fix_line_endings(text: str) -> str:
    """\\r\\r\\n gibi çift carriage return sorununu düzelt."""
    if not text:
        return ""
    text = text.replace('\r\r\n', '\n').replace('\r\n', '\n').replace('\r', '\n')
    return text.strip()


# ─────────────────────────────────────────────────────────────────────────────
# CSV Okuma
# ─────────────────────────────────────────────────────────────────────────────

def read_csv(path: Path) -> list[dict]:
    """CSV dosyasını oku, satır sonu sorunlarını düzelt."""
    rows = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        # universal newlines ile oku
        content = f.read()
        content = fix_line_endings(content)

    from io import StringIO
    reader = csv.DictReader(StringIO(content))
    for row in reader:
        # Her değerin satır sonunu temizle
        cleaned = {k: fix_line_endings(v or "") for k, v in row.items()}
        rows.append(cleaned)

    log.info(f"  {path.name}: {len(rows)} satır okundu")
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# DB Bağlantısı
# ─────────────────────────────────────────────────────────────────────────────

def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        log.info("MySQL bağlantısı başarılı ✓")
        return conn
    except mysql.connector.Error as e:
        log.error(f"MySQL bağlantı hatası: {e}")
        sys.exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# Import
# ─────────────────────────────────────────────────────────────────────────────

def ensure_schema(cursor) -> None:
    """Import oncesi veri kaybina yol acan kisa metin kolonlarini genislet."""
    cursor.execute("ALTER TABLE hadisler MODIFY ravi TEXT")
    cursor.execute("ALTER TABLE hadisler MODIFY bab TEXT")


def import_data(limit: int | None = None):
    log.info("=" * 60)
    log.info("Hadis Import Scripti Başlatıldı")
    log.info("=" * 60)

    # 1. CSV'leri oku
    log.info("\n[1/5] CSV dosyaları okunuyor...")
    ar_rows = read_csv(BUKHARI_AR)
    en_rows = read_csv(BUKHARI_EN)

    if limit:
        ar_rows = ar_rows[:limit]
        en_rows = en_rows[:limit]
        log.info(f"  Test modu: ilk {limit} hadis alınıyor")

    # id → satır map (İngilizce)
    en_map = {row["id"]: row for row in en_rows}

    # 2. DB bağlantısı
    log.info("\n[2/5] Veritabanına bağlanılıyor...")
    conn = get_connection()
    conn.autocommit = True
    cursor = conn.cursor()
    ensure_schema(cursor)

    # 3. Var olan verileri temizle (yeniden import)
    log.info("\n[3/5] Mevcut veriler temizleniyor...")
    cursor.execute("SET FOREIGN_KEY_CHECKS=0")
    for tbl in ["hadis_arapca", "hadis_ingilizce", "hadisler"]:
        cursor.execute(f"TRUNCATE TABLE {tbl}")
        log.info(f"  {tbl} temizlendi")
    cursor.execute("SET FOREIGN_KEY_CHECKS=1")
    conn.commit()

    # 4. Hadisleri yükle
    log.info("\n[4/5] Hadisler import ediliyor...")

    INSERT_HADIS = """
        INSERT INTO hadisler (id, hadis_no, kitap, bab, ravi, kaynak_link)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    INSERT_AR = """
        INSERT INTO hadis_arapca (hadis_id, sanad, hadith_detail, metin_temiz)
        VALUES (%s, %s, %s, %s)
    """
    INSERT_EN = """
        INSERT INTO hadis_ingilizce (hadis_id, sanad, hadith_detail, metin_temiz)
        VALUES (%s, %s, %s, %s)
    """

    skipped = 0
    imported = 0

    for ar_row in tqdm(ar_rows, desc="Import", unit="hadis"):
        row_id = ar_row.get("id", "").strip()
        if not row_id or not row_id.isdigit():
            skipped += 1
            continue

        hadis_id  = int(row_id)
        hadis_no  = f"BH-{row_id}"
        kitap     = normalize_display_text(ar_row.get("kitap", "Sahih al-Bukhari"), lang="en") or "Sahih al-Bukhari"
        bab       = normalize_display_text(ar_row.get("bab", ""), lang="en")
        ravi      = normalize_display_text(ar_row.get("ravi", ""), lang="en")
        kaynak    = normalize_display_text(ar_row.get("link", ""), lang="en")

        # Arapça
        ar_sanad  = normalize_display_text(ar_row.get("sanad", ""), lang="ar")
        ar_detail = normalize_display_text(ar_row.get("hadith_text", ""), lang="ar")
        ar_full   = f"{ar_sanad} {ar_detail}".strip()
        ar_temiz  = clean_arabic(ar_full)

        # İngilizce
        en_row    = en_map.get(row_id, {})
        en_sanad  = normalize_display_text(en_row.get("sanad", ""), lang="en")
        en_detail = en_row.get("hadith_text", "").strip()

        # English CSV'de full_clear_text veya hadith_text olabilir
        if not en_detail:
            en_detail = en_row.get("full_clear_text", "").strip()
        en_detail = normalize_display_text(en_detail, lang="en")
        en_full   = f"{en_sanad} {en_detail}".strip()
        en_temiz  = clean_english(en_full)

        try:
            cursor.execute(INSERT_HADIS, (hadis_id, hadis_no, kitap, bab, ravi, kaynak))
            cursor.execute(INSERT_AR,    (hadis_id, ar_sanad, ar_detail, ar_temiz))
            if en_detail:
                cursor.execute(INSERT_EN, (hadis_id, en_sanad, en_detail, en_temiz))
            imported += 1
        except mysql.connector.Error as e:
            log.warning(f"  Satır {row_id} atlandı: {e}")
            skipped += 1
            # conn.rollback() yapılmamalı, yoksa önceki tüm başarılı satırlar silinir.
            continue

    # 5. Özet
    log.info("\n[5/5] Import tamamlandı!")
    log.info(f"  ✓ Import edilen: {imported}")
    log.info(f"  ✗ Atlanan:       {skipped}")

    # Doğrulama
    cursor.execute("SELECT COUNT(*) FROM hadisler")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM hadis_arapca")
    total_ar = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM hadis_ingilizce")
    total_en = cursor.fetchone()[0]

    log.info(f"\n  Veritabanı özeti:")
    log.info(f"    hadisler       : {total}")
    log.info(f"    hadis_arapca   : {total_ar}")
    log.info(f"    hadis_ingilizce: {total_en}")

    cursor.close()
    conn.close()
    log.info("\nBağlantı kapatıldı. ✓")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hadis CSV → MySQL import")
    parser.add_argument("--limit", type=int, default=None,
                        help="Test için kaç hadis import edileceği (varsayılan: tümü)")
    args = parser.parse_args()
    import_data(limit=args.limit)
