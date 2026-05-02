#!/usr/bin/env python3
"""
Embedding Builder — MySQL → Sentence Transformers → Qdrant
===========================================================
Tüm Arapça ve İngilizce hadis metinlerini vektöre dönüştürür
ve Qdrant vector database'e yükler.

Kullanım:
    python scripts/build_embeddings.py
    python scripts/build_embeddings.py --lang ar   # sadece Arapça
    python scripts/build_embeddings.py --lang en   # sadece İngilizce
    python scripts/build_embeddings.py --batch 32  # batch boyutu
"""

import argparse
import logging
import os
import sys
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv
from tqdm import tqdm

# ── Path & Env ────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     os.getenv("MYSQL_HOST", "127.0.0.1"),
    "port":     int(os.getenv("MYSQL_PORT", 3306)),
    "database": os.getenv("MYSQL_DATABASE", "hadis_db"),
    "user":     os.getenv("MYSQL_USER", "hadis_user"),
    "password": os.getenv("MYSQL_PASSWORD", "hadis_pass"),
    "charset":  "utf8mb4",
}

QDRANT_HOST        = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT        = int(os.getenv("QDRANT_PORT", 6333))
COLLECTION_AR      = os.getenv("QDRANT_COLLECTION_AR", "hadisler_ar")
COLLECTION_EN      = os.getenv("QDRANT_COLLECTION_EN", "hadisler_en")
EMBEDDING_MODEL    = os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual-mpnet-base-v2")
EMBEDDING_DIM      = int(os.getenv("EMBEDDING_DIM", 768))
DEFAULT_BATCH_SIZE = 64


# ─────────────────────────────────────────────────────────────────────────────
# Qdrant kurulum
# ─────────────────────────────────────────────────────────────────────────────

def setup_qdrant_collections(client, recreate: bool = False):
    """Qdrant collection'larını oluştur (yoksa)."""
    from qdrant_client.models import Distance, VectorParams

    for col in [COLLECTION_AR, COLLECTION_EN]:
        exists = any(c.name == col for c in client.get_collections().collections)
        if exists and recreate:
            client.delete_collection(col)
            exists = False

        if not exists:
            client.create_collection(
                collection_name=col,
                vectors_config=VectorParams(
                    size=EMBEDDING_DIM,
                    distance=Distance.COSINE,
                ),
            )
            log.info(f"  Collection oluşturuldu: {col}")
        else:
            log.info(f"  Collection mevcut, atlanıyor: {col}")


# ─────────────────────────────────────────────────────────────────────────────
# MySQL'den veri çekme
# ─────────────────────────────────────────────────────────────────────────────

def fetch_hadisler(lang: str) -> list[dict]:
    """
    MySQL'den hadis ID + metin çek.
    lang: 'ar' veya 'en'
    """
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    if lang == "ar":
        cursor.execute("""
            SELECT h.id, ha.hadith_detail AS metin
            FROM hadisler h
            JOIN hadis_arapca ha ON ha.hadis_id = h.id
            WHERE ha.hadith_detail IS NOT NULL AND ha.hadith_detail != ''
            ORDER BY h.id
        """)
    else:
        cursor.execute("""
            SELECT h.id, hi.hadith_detail AS metin
            FROM hadisler h
            JOIN hadis_ingilizce hi ON hi.hadis_id = h.id
            WHERE hi.hadith_detail IS NOT NULL AND hi.hadith_detail != ''
            ORDER BY h.id
        """)

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    log.info(f"  {lang.upper()}: {len(rows)} hadis çekildi")
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# Embedding üretimi ve Qdrant yükleme
# ─────────────────────────────────────────────────────────────────────────────

def encode_and_upload(
    model,
    client,
    collection_name: str,
    rows: list[dict],
    batch_size: int,
):
    """Batch'ler halinde encode edip Qdrant'a yükle."""
    from qdrant_client.models import PointStruct

    total    = len(rows)
    uploaded = 0

    for i in tqdm(range(0, total, batch_size), desc=f"Yükleniyor ({collection_name})", unit="batch"):
        batch = rows[i : i + batch_size]
        texts = [r["metin"][:512] for r in batch]  # max 512 token

        # Embedding üret
        vectors = model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=True,  # cosine için normalize
        ).tolist()

        # Qdrant point'lerini hazırla
        points = [
            PointStruct(
                id=int(row["id"]),
                vector=vec,
                payload={"hadis_id": int(row["id"])},
            )
            for row, vec in zip(batch, vectors)
        ]

        # Qdrant'a yükle (upsert — tekrar çalıştırılabilir)
        client.upsert(collection_name=collection_name, points=points)
        uploaded += len(batch)

    log.info(f"  ✓ {uploaded} hadis {collection_name} collection'ına yüklendi")
    return uploaded


# ─────────────────────────────────────────────────────────────────────────────
# Ana fonksiyon
# ─────────────────────────────────────────────────────────────────────────────

def main(lang: str = "both", batch_size: int = DEFAULT_BATCH_SIZE, recreate: bool = False):
    log.info("=" * 60)
    log.info("Embedding Builder Başlatıldı")
    log.info(f"  Model   : {EMBEDDING_MODEL}")
    log.info(f"  Qdrant  : {QDRANT_HOST}:{QDRANT_PORT}")
    log.info(f"  Dil     : {lang}")
    log.info(f"  Batch   : {batch_size}")
    log.info("=" * 60)

    # 1. Qdrant bağlantısı
    log.info("\n[1/4] Qdrant'a bağlanılıyor...")
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        client.get_collections()  # bağlantı testi
        log.info("  Qdrant bağlantısı başarılı ✓")
    except Exception as e:
        log.error(f"  Qdrant bağlantı hatası: {e}")
        sys.exit(1)

    # 2. Collection'ları kur
    log.info("\n[2/4] Qdrant collection'ları hazırlanıyor...")
    setup_qdrant_collections(client, recreate=recreate)

    # 3. Modeli yükle
    log.info(f"\n[3/4] Model yükleniyor: {EMBEDDING_MODEL}")
    log.info("  (İlk indirme ~420MB sürebilir, lütfen bekleyin...)")
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(EMBEDDING_MODEL)
        log.info("  Model yüklendi ✓")
    except Exception as e:
        log.error(f"  Model yükleme hatası: {e}")
        sys.exit(1)

    # 4. Encode & Upload
    log.info("\n[4/4] Hadisler encode ediliyor ve Qdrant'a yükleniyor...")

    langs_to_process = ["ar", "en"] if lang == "both" else [lang]

    for l in langs_to_process:
        col = COLLECTION_AR if l == "ar" else COLLECTION_EN
        log.info(f"\n  [{l.upper()}] Veriler MySQL'den çekiliyor...")
        rows = fetch_hadisler(l)

        if not rows:
            log.warning(f"  [{l.upper()}] Veri bulunamadı, atlanıyor")
            continue

        encode_and_upload(model, client, col, rows, batch_size)

    # Özet
    log.info("\n" + "=" * 60)
    for col in ([COLLECTION_AR, COLLECTION_EN] if lang == "both" else [COLLECTION_AR if lang == "ar" else COLLECTION_EN]):
        info = client.get_collection(col)
        log.info(f"  {col}: {info.points_count} vektör")
    log.info("=" * 60)
    log.info("✓ Embedding işlemi tamamlandı!")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hadis Embedding Builder")
    parser.add_argument("--lang",     choices=["ar", "en", "both"], default="both")
    parser.add_argument("--batch",    type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--recreate", action="store_true",
                        help="Mevcut collection'ları sil ve yeniden oluştur")
    args = parser.parse_args()
    main(lang=args.lang, batch_size=args.batch, recreate=args.recreate)
