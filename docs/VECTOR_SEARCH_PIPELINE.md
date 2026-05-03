# Vector Search Pipeline Documentation
## HadithSearch - Vektör Arama Pipeline'ı

---

## 1. Genel Bakış

Vektör arama pipeline'ı, metinleri matematiksel vektörlere dönüştürüp 
benzerlik araması yapma sürecidir. HadithSearch'te bu süreç 3 aşamadan oluşur:

1. **Embedding Üretimi** (Encoding)
2. **Vektör Saklama** (Storage)
3. **Benzerlik Araması** (Search)

---

## 2. Mimari Diyagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    VEKTÖR ARAMA PIPELINE                                    │
└─────────────────────────────────────────────────────────────────────────────┘

Faz 1: EMBEDDING ÜRETİMİ (Index Time)
────────────────────────────────────────

Ham Metin (Arapça/İngilizce)
    │
    │ 1. Temizleme
    │    - Hareke kaldırma (Arapça)
    │    - Noktalama kaldırma
    │    - Normalize
    ▼
┌─────────────────┐
│  Temiz Metin    │
└────────┬────────┘
         │
         │ 2. Tokenize
         │    - WordPiece (BERT tabanlı)
         ▼
┌─────────────────┐     ┌─────────────────────────────┐
│  Token IDs      │────►│  Sentence Transformers      │
│  [101, 234, ...]│     │  Model:                       │
└─────────────────┘     │  paraphrase-multilingual-   │
                        │  mpnet-base-v2                │
                        │                               │
                        │  • 768 hidden units          │
                        │  • 12 transformer layers       │
                        │  • Mean pooling               │
                        └───────────────┬───────────────┘
                                        │
                                        │ 3. Forward Pass
                                        │    + Normalize
                                        ▼
                              ┌─────────────────┐
                              │  Embedding      │
                              │  [0.023, -0.156, │
                              │   0.089, ...]    │
                              │  768 dimensions │
                              │  Float32        │
                              └────────┬────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │  L2 Normalize   │
                              │  │v│ = 1        │
                              └────────┬────────┘
                                       │
                                       ▼
Faz 2: VEKTÖR SAKLAMA
────────────────────────────────────────
                              ┌─────────────────┐
                              │  Qdrant Upsert  │
                              │                 │
                              │  Collection:  │
                              │  hadisler_ar    │
                              │  veya           │
                              │  hadisler_en    │
                              └────────┬────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              QDRANT VECTOR DB                               │
│                                                                             │
│  Collection: hadisler_ar (Arapça)        Collection: hadisler_en (İngilizce)│
│  ┌─────────────────────────────────┐    ┌────────────────────────────────┐│
│  │ Points: 7,277                   │    │ Points: 7,277                  ││
│  │ Dimension: 768                  │    │ Dimension: 768                 ││
│  │ Distance: Cosine                │    │ Distance: Cosine               ││
│  │                                 │    │                                ││
│  │ HNSW Index:                     │    │ HNSW Index:                    ││
│  │ • m: 16                         │    │ • m: 16                        ││
│  │ • ef_construct: 100             │    │ • ef_construct: 100            │
│  │ • ef: 100                       │    │ • ef: 100                      ││
│  └─────────────────────────────────┘    └────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘

Faz 3: BENZERLİK ARAMASI (Query Time)
────────────────────────────────────────

Kullanıcı Sorgusu
    │
    │ Aynı Pipeline
    ▼
┌─────────────────┐
│ Sorgu Embedding │
│ [0.034, 0.189, │
│  -0.056, ...]   │
│ 768 dimensions  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           QDRANT SEARCH                                     │
│                                                                             │
│  HNSW Approximate Nearest Neighbor Search:                                 │
│                                                                             │
│  1. Entry Point'ten başla                                                  │
│  2. En yakın komşulara git (greedy)                                         │
│  3. ef (exploration factor) kadar adım at                                  │
│  4. En yakın k vektörü döndür                                              │
│                                                                             │
│  Cosine Similarity:                                                        │
│  score = (A · B) / (|A| × |B|)                                             │
│  (L2 normalize edildiği için |A| = |B| = 1)                                │
│  score = A · B (dot product)                                                │
└─────────────────────────┬───────────────────────────────────────────────────┘
                          │
                          ▼
                  ┌─────────────────┐
                  │  Sonuçlar       │
                  │  [{id, score}]  │
                  │  Top-K: 50-100  │
                  └─────────────────┘
```

---

## 3. Embedding Modeli Detayları

### 3.1 Model Seçimi

**Model:** `paraphrase-multilingual-mpnet-base-v2`

**Neden bu model?**
- ✅ Çok dilli (Arapça + İngilizce aynı uzayda)
- ✅ 768 boyut (dengi boyut/performans)
- ✅ Apache 2.0 lisans (ücretsiz)
- ✅ HuggingFace'de yaygın kullanım
- ✅ Yüksek STS (Semantic Textual Similarity) skorları

### 3.2 Model Mimarisi

```
paraphrase-multilingual-mpnet-base-v2
├── Base: microsoft/mpnet-base
├── Pooling: Mean pooling
├── Normalize: L2 normalization
│
├── Architecture:
│   ├── Layers: 12 (transformer blocks)
│   ├── Hidden size: 768
│   ├── Attention heads: 12
│   ├── Parameters: ~278M
│   ├── Vocab size: 250,000+ (multilingual)
│   └── Max sequence: 512 tokens
│
└── Training:
    ├── Paraphrase detection
    ├── Semantic similarity
    ├── NLI (Natural Language Inference)
    └── Multilingual corpus
```

### 3.3 Embedding Süreci

```python
from sentence_transformers import SentenceTransformer

# Model yükleme (lazy singleton)
model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

# Embedding üretme
text = "The Prophet said about prayer..."
embedding = model.encode(
    text,
    normalize_embeddings=True,  # L2 normalize
    show_progress_bar=False,
    convert_to_numpy=True
)

# Output: numpy array (768,)
# Değerler: [-0.023, 0.156, -0.089, ...]
# Norm: 1.0 (normalize edilmiş)
```

### 3.4 Tokenizasyon

```python
# WordPiece tokenizasyonu
# Örnek: "prayer" → ["pray", "##er"]
# Örnek: "الصلاة" → ["ال", "صل", "##اة"]

tokens = model.tokenizer.encode(text)
# Output: [101, 2428, 4567, 102] (token IDs)
# 101: [CLS], 102: [SEP]

# Max 512 tokens (model limit)
# Uzun metinler truncate edilir
```

---

## 4. Qdrant Yapılandırması

### 4.1 Koleksiyon Tanımları

```python
# Arapça koleksiyon
client.create_collection(
    collection_name="hadisler_ar",
    vectors_config=VectorParams(
        size=768,
        distance=Distance.COSINE,
        hnsw_config=HnswConfigDiff(
            m=16,              # Connections per layer
            ef_construct=100,  # Build time accuracy
        )
    )
)

# İngilizce koleksiyon
client.create_collection(
    collection_name="hadisler_en",
    vectors_config=VectorParams(
        size=768,
        distance=Distance.COSINE
    )
)
```

### 4.2 HNSW Algoritması

**Hierarchical Navigable Small World (HNSW)**

```
Layer 3 (sparse):    O O       O    O    ← Entry point
                    /|\      /|\  /|
Layer 2:           O-O-O    O-O-O-O-O   ← Long jumps
                  /| |\    /| | | |
Layer 1:         O-O-O-O--O-O-O-O-O-O  ← Short hops
                /| | | |  /| | | | |
Layer 0 (dense): O-O-O-O--O-O-O-O-O-O  ← All vectors
                (base layer: tüm vektörler)

Parametreler:
- m=16: Her düğümde max 16 bağlantı
- ef_construct=100: İnşaat sırasında 100 komşu ara
- ef=100: Sorgu sırasında 100 komşu ara
```

**Neden HNSW?**
- ⚡ O(log n) arama karmaşıklığı (brute force O(n))
- 🎯 Yüksek recall (>95% brute force'a göre)
- 💾 Bellek verimli (graph yapısı)

### 4.3 Point Yapısı

```python
{
    "id": 123,                    # hadis_id (int)
    "vector": [0.023, -0.156, ...],  # 768 float
    "payload": {                  # Metadata (opsiyonel)
        "hadis_no": "BH-456",
        "kitap": "Sahih al-Bukhari",
        "bab": "Book of Prayer"
    }
}
```

---

## 5. Arama Süreci Detaylı

### 5.1 Query Encoding

```python
async def vector_search(query: str, lang: str, top_k: int = 50):
    # 1. Dil bazlı koleksiyon seç
    collection = "hadisler_ar" if lang == "ar" else "hadisler_en"
    
    # 2. Sorguyu embedding'e çevir (thread'de çalıştır)
    query_vector = await asyncio.to_thread(
        _encode_query_sync, 
        query
    )
    
    # 3. Qdrant'ta ara
    results = await asyncio.to_thread(
        _qdrant_search_sync,
        collection,
        query_vector,
        top_k
    )
    
    return [{"hadis_id": r.id, "score": r.score} for r in results]
```

### 5.2 Cosine Similarity

```
Formül:
cosine_similarity(A, B) = (A · B) / (|A| × |B|)

A ve B L2 normalize edilmişse:
|A| = |B| = 1

cosine_similarity(A, B) = A · B  (dot product)

Değer aralığı: [-1, 1]
- 1: Tamamen aynı yönde
- 0: Dik (ilişkisiz)
- -1: Tamamen zıt

Qdrant'ta normalize edilmiş vektörler kullanıldığı için:
score = dot_product (0.0 - 1.0 arası)
```

### 5.3 Search Request

```python
# Qdrant search request
res = client.query_points(
    collection_name="hadisler_en",
    query=query_vector,           # [0.023, -0.156, ...]
    limit=top_k,                  # 50-100
    with_payload=False,           # Sadece ID ve score
    score_threshold=0.0,           # Tüm sonuçlar
)

# Response
points = [
    ScoredPoint(
        id=123,
        version=1,
        score=0.854321,           # Cosine similarity
        payload=None,
        vector=None
    ),
    ...
]
```

---

## 6. Hybrid Search (BM25 + Vector)

### 6.1 Paralel Arama

```python
async def hybrid_search(db, query, dil, sayfa, limit):
    # Paralel sorgular
    bm25_task = bm25_search(db, query, dil=dil, limit=100)
    vector_task = vector_search(query, lang=dil, top_k=100)
    
    # Eşzamanlı çalıştır
    (bm25_results, _), vector_results = await asyncio.gather(
        bm25_task, 
        vector_task
    )
```

### 6.2 RRF Fusion

```python
def reciprocal_rank_fusion(bm25_results, vector_results):
    """
    Reciprocal Rank Fusion
    
    BM25 rank: 1, 2, 3, 4, 5, ...
    Vector rank: 1, 2, 3, ...
    
    RRF_score = Σ 1/(k + rank)
    k = 60 (outlier'ları bastırır)
    """
    
    scores = {}
    k = 60
    
    # BM25 skorları (weight: 0.4)
    for rank, item in enumerate(bm25_results, start=1):
        hid = item["id"]
        scores[hid] = scores.get(hid, 0) + 0.4 * (1.0 / (k + rank))
    
    # Vector skorları (weight: 0.6)
    for rank, item in enumerate(vector_results, start=1):
        hid = item["hadis_id"]
        scores[hid] = scores.get(hid, 0) + 0.6 * (1.0 / (k + rank))
    
    # Sırala
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

### 6.3 Neden Farklı Weight'ler?

```
BM25 weight: 0.4
Vector weight: 0.6

Neden vektör ağırlığı daha yüksek?
- Semantik arama daha doğru sonuçlar veriyor
- BM25 tam eşleşme için kullanılır
- Hibrit yaklaşımda anlam önceliklidir

Ağırlıklar tuning ile belirlenebilir:
- 0.5/0.5: Dengeli
- 0.3/0.7: Semantik odaklı
- 0.7/0.3: Kelime odaklı
```

---

## 7. Performans Karakteristikleri

### 7.1 Zaman Karmaşıklığı

| İşlem | Karmaşıklık | Süre (7,727 hadis) |
|-------|-------------|-------------------|
| Embedding üretimi | O(n) | ~50ms / metin |
| HNSW arama | O(log n) | ~10-20ms |
| Brute force | O(n × d) | ~500ms (çok yavaş) |
| MySQL FULLTEXT | O(log n) | ~50-100ms |

n = vektör sayısı, d = boyut (768)

### 7.2 Bellek Kullanımı

```
Her vektör: 768 × 4 byte = 3 KB
Toplam: 7,727 × 3 KB = ~23 MB (ham)

HNSW index overhead: ~2-3x
Toplam bellek: ~70-100 MB

Model belleği: ~1 GB (sentence-transformers)
```

### 7.3 Latency Optimizasyonları

1. **Lazy Model Loading**: İlk sorguda model yüklenir
2. **LRU Cache**: Model singleton (lru_cache)
3. **Async Encoding**: Thread pool'da çalıştır
4. **Batch Upsert**: Qdrant'a toplu yazma

---

## 8. Fallback Mekanizması

### 8.1 Qdrant Hazır Değilse

```python
async def hybrid_search(...):
    # Qdrant hazır mı kontrol et
    qdrant_ok = await is_qdrant_ready(dil)
    
    if not qdrant_ok:
        # Sadece BM25 kullan
        sonuclar, toplam = await bm25_search(db, query, ...)
        return sonuclar, toplam, "bm25_only"
```

### 8.2 is_qdrant_ready

```python
async def is_qdrant_ready(lang: str) -> bool:
    try:
        col = "hadisler_ar" if lang == "ar" else "hadisler_en"
        info = client.get_collection(col)
        return (info.points_count or 0) > 0
    except Exception:
        return False
```

---

## 9. Veri İçe Aktarma Pipeline'ı

### 9.1 CSV'den Qdrant'a

```python
def import_to_qdrant(csv_path, lang):
    """
    1. CSV dosyasını oku
    2. Her satır için:
       a. Metni temizle
       b. Embedding üret
       c. Qdrant point oluştur
    3. Batch upsert (100'erli)
    """
    
    points = []
    for row in read_csv(csv_path):
        # Metin temizleme
        clean_text = normalize_text(row['text'], lang)
        
        # Embedding
        vector = model.encode(clean_text, normalize_embeddings=True)
        
        # Point oluştur
        point = PointStruct(
            id=row['hadis_id'],
            vector=vector.tolist(),
            payload={
                "hadis_no": row['hadis_no'],
                "kitap": row['kitap']
            }
        )
        points.append(point)
        
        # Batch upsert (her 100'de bir)
        if len(points) >= 100:
            client.upsert(collection_name=f"hadisler_{lang}", points=points)
            points = []
    
    # Kalanları upsert et
    if points:
        client.upsert(collection_name=f"hadisler_{lang}", points=points)
```

---

## 10. Karşılaştırma: Arama Modları

### 10.1 BM25 vs Vector vs Hybrid

| Özellik | BM25 | Vector | Hybrid |
|---------|------|--------|--------|
| **Anlama** | Kelime eşleşmesi | Anlam benzerliği | Her ikisi |
| **Eşleşme** | Tam kelime | Konsept | Akıllı |
| **Speed** | ~50ms | ~300ms | ~400ms |
| **Recall** | Orta | Yüksek | En yüksek |
| **Precision** | Yüksek | Orta | Yüksek |
| **Use Case** | Spesifik arama | Genel arama | Varsayılan |

### 10.2 Örnek Sonuçlar

Sorgu: "giving to the poor"

| Mod | 1. Sonuç | 2. Sonuç | 3. Sonuç |
|-----|----------|----------|----------|
| BM25 | charity | alms | zakat |
| Vector | generosity | kindness | helping |
| Hybrid | charity | generosity | zakat |

---

## 11. Gelecek İyileştirmeler

### 11.1 Re-ranking

```
İlk 20 sonuç → CrossEncoder → Yeniden sırala

CrossEncoder daha doğru ama yavaş:
- Input: (query, document) çifti
- Output: tek skor
- Süre: ~100ms / çift

Sadece ilk 20 için kullanılabilir.
```

### 11.2 Query Expansion

```
Kullanıcı: "fasting"
Sistem: "fasting OR sawm OR ramadan OR roza"

Embedding space'te yakın kelimeleri bul:
synonyms = find_similar_terms("fasting", top_k=5)
expanded_query = "fasting " + " ".join(synonyms)
```

### 11.3 Multi-vector Approach

```
Her hadis için birden fazla vektör:
- Tam metin vektörü
- Özet vektörü
- Konu etiketi vektörü

Sorgu zamanında:
- Tam metin vektörü ile ara
- Özet vektörü ile ara
- Sonuçları birleştir
```

---

## 12. Kaynaklar

- **Sentence Transformers**: https://www.sbert.net/
- **Qdrant Docs**: https://qdrant.tech/documentation/
- **HNSW Paper**: https://arxiv.org/abs/1603.09320
- **RRF Paper**: https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf
- **MPNet Paper**: https://arxiv.org/abs/2004.09297

---

**Versiyon**: 1.0.0
**Son Güncelleme**: Mayıs 2026
