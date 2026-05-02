# Hadis Semantik Arama Sistemi - Gerekli Beceriler ve Teknolojiler

## Proje Özeti
Sahih Bukhari ve Sahih Muslim külliyatları üzerinde çalışan, NLP tabanlı hibrit (BM25 + Semantik) arama sistemi. Arapça ve İngilizce dil desteği.

---

## 1. Backend Geliştirme

### FastAPI
- **Seviye**: İleri düzey
- **Kullanım**: API endpoint'leri (`/ara`, `/hadis/{id}`, `/kategoriler`)
- **Gereksinimler**:
  - Async/await yapısı
  - Pydantic model validasyonu
  - Otomatik OpenAPI dokümantasyonu (`/docs`)
  - Dependency injection
  - Exception handling
- **Kaynak**: [FastAPI Documentation](https://fastapi.tiangolo.com/)

### Python
- **Seviye**: İleri düzey
- **Versiyon**: 3.9+
- **Gereksinimler**:
  - Tip hinting (typing module)
  - Asenkron programlama (asyncio)
  - Veri yapıları ve algoritmalar
  - JSON/CSV veri işleme

---

## 2. Doğal Dil İşleme (NLP)

### Sentence Transformers
- **Seviye**: Orta-İleri
- **Model**: `paraphrase-multilingual-mpnet-base-v2`
- **Görevler**:
  - Metinleri 768 boyutlu vektörlere dönüştürme (embedding)
  - Çok dilli destek (Arapça, İngilizce)
  - Cosine similarity hesaplama
- **Kaynak**: [Sentence Transformers Documentation](https://www.sbert.net/)

### CrossEncoder (Re-ranking)
- **Seviye**: Orta
- **Görevler**:
  - Sorgu-doküman çiftlerini değerlendirme
  - İlk 20 adayın yeniden sıralanması
  - Yüksek doğruluklu alaka düzeyi skorlama
- **Kaynak**: [Cross-Encoders - SBERT](https://www.sbert.net/examples/applications/cross-encoder/README.html)

### Metin Ön İşleme
- **Arapça Temizleme**:
  - Harekeleri kaldırma (تَشْكِيل) - opsiyonel
  - Elif varyasyonları normalize etme (ٱإأآا → ا)
  - Te ve he normalize etme (ة → ه)
  - Noktalama temizleme
  - Boşluk normalizasyonu
- **İngilizce Temizleme**:
  - Küçük harf dönüşümü
  - Noktalama temizleme
  - Boşluk normalizasyonu
- **Kütüphaneler**: `regex`, `pyarabic` (opsiyonel)

---

## 3. Veritabanı Yönetimi

### MySQL 8.0
- **Seviye**: İleri
- **Karakter Seti**: `utf8mb4` + `utf8mb4_unicode_ci`
- **Görevler**:
  - Hadis metadata yönetimi
  - Arapça ve İngilizce metin saklama
  - FULLTEXT indeks ile BM25 benzeri arama
  - Kategori ilişkileri (many-to-many)

### MySQL Şeması (Son Karar)

#### Ana Metadata Tablosu
```sql
CREATE TABLE hadisler (
    id INT PRIMARY KEY AUTO_INCREMENT,
    hadis_no VARCHAR(20) NOT NULL,        -- Örn: "BH-1", "SM-1901"
    kitap VARCHAR(50) NOT NULL,           -- 'Sahih Bukhari', 'Sahih Muslim'
    bab VARCHAR(100),                     -- 'Kitab al-Iman', 'Book of Prayer'
    ravi VARCHAR(100),                    -- 'Umar ibn al-Khattab'
    kaynak_link VARCHAR(500),             -- https://sunnah.com/bukhari/1
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_hadis_no (hadis_no),
    INDEX idx_kitap (kitap),
    INDEX idx_ravi (ravi)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### Arapça Metin Tablosu
```sql
CREATE TABLE hadis_arapca (
    hadis_id INT PRIMARY KEY,
    sanad TEXT,                           -- Rivayet zinciri
    hadith_detail TEXT NOT NULL,          -- Metnin kendisi (matan)
    metin_temiz TEXT NOT NULL,            -- sanad + hadith_detail (temizlenmiş)

    FOREIGN KEY (hadis_id) REFERENCES hadisler(id) ON DELETE CASCADE,
    FULLTEXT INDEX ft_arapca (metin_temiz) WITH PARSER ngram
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### İngilizce Metin Tablosu
```sql
CREATE TABLE hadis_ingilizce (
    hadis_id INT PRIMARY KEY,
    sanad TEXT,                           -- Narrator chain
    hadith_detail TEXT NOT NULL,          -- Hadith text
    metin_temiz TEXT NOT NULL,            -- Cleaned text for search

    FOREIGN KEY (hadis_id) REFERENCES hadisler(id) ON DELETE CASCADE,
    FULLTEXT INDEX ft_ingilizce (metin_temiz)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### Kategoriler (Many-to-Many)
```sql
CREATE TABLE kategoriler (
    id INT PRIMARY KEY AUTO_INCREMENT,
    kategori_adi VARCHAR(50) NOT NULL,
    kategori_adi_en VARCHAR(50),
    UNIQUE KEY uk_kategori (kategori_adi)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE hadis_kategoriler (
    hadis_id INT NOT NULL,
    kategori_id INT NOT NULL,
    PRIMARY KEY (hadis_id, kategori_id),
    FOREIGN KEY (hadis_id) REFERENCES hadisler(id) ON DELETE CASCADE,
    FOREIGN KEY (kategori_id) REFERENCES kategoriler(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### MySQL FULLTEXT Özellikleri
- **Arapça**: `WITH PARSER ngram` - karakter tabanlı tokenizasyon
- **İngilizce**: Varsayılan parser - kelime tabanlı tokenizasyon
- **ngram_token_size**: Varsayılan 2, `my.cnf` ile ayarlanabilir

### SQLAlchemy (ORM)
- **Seviye**: Orta-İleri
- **Kullanım**: MySQL ile Python arasında ORM katmanı
- **Gereksinimler**:
  - Model tanımlama (declarative base)
  - Relationship tanımlama (one-to-one, many-to-many)
  - Async destek (`asyncmy` driver)
  - Session ve transaction yönetimi
- **Kaynak**: [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

### Qdrant (Vektör Veritabanı)
- **Seviye**: Orta
- **Görevler**:
  - 768 boyutlu vektörlerin saklanması
  - HNSW algoritması ile hızlı benzerlik arama
  - Payload filtering (kategori, kitap filtresi)
  - Dil başına ayrı collection: `hadisler_ar`, `hadisler_en`
- **Kaynak**: [Qdrant Documentation](https://qdrant.tech/documentation/)

---

## 4. Bilgi Erişim Algoritmaları

### BM25 (Best Match 25)
- **Seviye**: Orta
- **Kullanım**: MySQL FULLTEXT ile kelime frekansına dayalı arama
- **Arapça**: `MATCH(...) AGAINST(... IN NATURAL LANGUAGE MODE)`
- **İngilizce**: `MATCH(...) AGAINST(... IN NATURAL LANGUAGE MODE)`
- **Parametreler**:
  - `ft_min_word_len`: Minimum kelime uzunluğu
  - `ngram_token_size`: Arapça için karakter n-gram boyutu
- **Kaynak**: [MySQL FULLTEXT Search](https://dev.mysql.com/doc/refman/8.0/en/fulltext-search.html)

### RRF (Reciprocal Rank Fusion)
- **Seviye**: Orta
- **Formül**: `RRF_skoru(d) = Σ 1 / (k + rank_i(d))` (k=60)
- **Görev**: BM25 (MySQL) ve Semantic (Qdrant) sonuçlarını birleştirme
- **Kaynak**: [Reciprocal Rank Fusion Paper](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)

---

## 5. DevOps ve Altyapı

### Docker
- **Seviye**: Orta
- **Görevler**:
  - MySQL 8.0 container'ı
  - Qdrant container'ı
  - FastAPI uygulaması container'ı
  - Docker Compose ile multi-container orchestration
- **Kaynak**: [Docker Documentation](https://docs.docker.com/)

### Docker Compose
- **Seviye**: Orta
- **Servisler**:
  - `app`: FastAPI uygulaması
  - `db`: MySQL 8.0 (utf8mb4 ayarları)
  - `qdrant`: Vektör veritabanı
- **Kaynak**: [Docker Compose Documentation](https://docs.docker.com/compose/)

---

## 6. Veri Hazırlama ve İşleme

### Veri Temizleme
- JSON/CSV parsing
- Encoding düzeltme (UTF-8)
- Eksik veri yönetimi
- Duplicate kontrolü
- Sanad ve Hadith Detail ayrımı

### Temizleme Pipeline
```
Ham Veri (JSON/CSV)
    │
    ├── Ayrıştırma
    │   ├── hadis_no, kitap, bab, ravi, kaynak_link → hadisler
    │   ├── sanad, hadith_detail → hadis_arapca / hadis_ingilizce
    │
    ├── Temizleme
    │   ├── Arapça: hareke kaldırma, elif normalize, noktalama
    │   ├── İngilizce: küçük harf, noktalama
    │   └── sanad + hadith_detail → metin_temiz
    │
    └── Indexleme
        ├── MySQL: INSERT + FULLTEXT index
        └── Qdrant: model.encode() → vector upsert
```

---

## 7. API Tasarımı ve Dokümantasyon

### REST API Prensipleri
- HTTP metodları (GET, POST)
- Durum kodları (200, 400, 404, 500)
- Query parametreleri (`q`, `dil`, `kategori`, `sayfa`)
- JSON response formatı

### Endpoint Örnekleri
```
GET /ara?q=النية&dil=ar&kategori=ibadet&sayfa=1
GET /hadis/BH-1
GET /kategoriler
```

### Response Yapısı
```json
{
  "sorgu": "النية",
  "dil": "ar",
  "sayfa": 1,
  "sonuclar": [
    {
      "id": 1,
      "hadis_no": "BH-1",
      "kitap": "Sahih Bukhari",
      "bab": "Kitab al-Iman",
      "ravi": "Umar ibn al-Khattab",
      "kaynak_link": "https://sunnah.com/bukhari/1",
      "arapca": {
        "sanad": "حَدَّثَنَا الْحُمَيْدِيُّ...",
        "hadith_detail": "إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ..."
      },
      "ingilizce": {
        "sanad": "Narrated by Al-Humaydi...",
        "hadith_detail": "The deeds are considered by the intentions..."
      },
      "skor": 0.95
    }
  ]
}
```

### OpenAPI/Swagger
- Otomatik API dokümantasyonu
- Endpoint test arayüzü
- Şema tanımları

---

## 8. Test ve Değerlendirme

### Birim Testleri
- **Kütüphane**: `pytest`
- **Kapsam**: API endpoint'leri, veritabanı sorguları, algoritmalar

### Entegrasyon Testleri
- End-to-end arama akışı
- MySQL bağlantıları
- Qdrant bağlantıları
- Docker container'ları

### Performans Metrikleri
- **Precision**: İlk 10 sonuçtan kaç tanesi alakalı?
- **Recall**: Tüm alakalı hadislerden kaçı bulundu?
- **Latency**: Sorgu yanıt süresi (hedef: <500ms CPU, <100ms GPU)

---

## 9. Güvenlik

### API Güvenliği
- Rate limiting (istek sınırlama)
- Input validation (SQL injection, XSS önleme)
- CORS politikaları

### Veri Güvenliği
- Hassas veri şifreleme (gerekirse)
- Backup stratejisi

---

## 10. Önerilen Öğrenme Yolu

### Başlangıç (Hafta 1-2)
1. FastAPI temelleri
2. MySQL 8.0 temelleri ve FULLTEXT index
3. Python async/await
4. UTF-8 ve karakter encoding

### Orta Seviye (Hafta 3-4)
1. Sentence Transformers kullanımı
2. Qdrant kurulumu ve temel sorgular
3. Arapça metin işleme (normalize, hareke)
4. BM25 implementasyonu (MySQL FULLTEXT)

### İleri Seviye (Hafta 5-6)
1. RRF Fusion implementasyonu
2. CrossEncoder re-ranking
3. Docker ve Docker Compose
4. SQLAlchemy ORM

### Uzmanlık (Hafta 7-8)
1. Performans optimizasyonu
2. Ölçeklenebilirlik stratejileri
3. Monitoring ve logging
4. Çok dilli arama optimizasyonu

---

## Teknoloji Stack Özeti

| Katman | Teknoloji | Amaç |
|--------|-----------|------|
| API | FastAPI | HTTP endpoint'leri |
| NLP | Sentence Transformers | Embedding üretimi |
| NLP | CrossEncoder | Re-ranking |
| Arama | MySQL FULLTEXT | BM25 benzeri kelime araması |
| Arama | Qdrant | Semantik vektör araması |
| Birleştirme | RRF | Sonuç fusion |
| Veritabanı | MySQL 8.0 | Metadata ve metin saklama |
| Vektör DB | Qdrant | Semantik arama |
| ORM | SQLAlchemy + asyncmy | Veritabanı erişimi |
| Container | Docker | İzolasyon |
| Test | pytest | Kalite kontrol |

---

## Veritabanı Şema Özeti

| Tablo | Amaç | Dil |
|-------|------|-----|
| `hadisler` | Metadata (hadis_no, kitap, ravi, kaynak_link) | Bağımsız |
| `hadis_arapca` | Sanad + Hadith Detail (orijinal + temiz) | Arapça |
| `hadis_ingilizce` | Sanad + Hadith Detail (orijinal + temiz) | İngilizce |
| `kategoriler` | Kategori listesi | Çok dilli |
| `hadis_kategoriler` | Many-to-many ilişki | - |

---

## Kaynaklar ve Referanslar

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [Qdrant Docs](https://qdrant.tech/documentation/)
- [MySQL 8.0 Docs](https://dev.mysql.com/doc/)
- [MySQL FULLTEXT Search](https://dev.mysql.com/doc/refman/8.0/en/fulltext-search.html)
- [MySQL ngram Parser](https://dev.mysql.com/doc/refman/8.0/en/fulltext-search-ngram.html)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [asyncmy - Async MySQL Driver](https://github.com/long2ice/asyncmy)
- [Docker Docs](https://docs.docker.com/)
- [RRF Paper](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)
- [PyArabic - Arapça NLP Kütüphanesi](https://github.com/linuxscout/pyarabic)
