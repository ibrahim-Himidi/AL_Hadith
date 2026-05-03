# Database Design Documentation
## HadithSearch - Veritabanı Tasarımı

---

## 1. Genel Bakış

HadithSearch iki veritabanı kullanır:
- **MySQL 8.0**: Yapısal veri (metadata, kullanıcılar, metinler)
- **Qdrant**: Vektör verileri (sembantik arama embedding'leri)

Bu doküman MySQL şemasını kapsar.

---

## 2. ER Diyagramı (Entity Relationship)

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     users       │       │    hadisler     │       │  hadis_arapca  │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ PK id           │       │ PK id           │◄──────│ PK/FK hadis_id  │
│ email (unique)  │       │ hadis_no        │       │ sanad           │
│ hashed_password │       │ kitap           │       │ hadith_detail   │
│ full_name       │       │ kitap_id        │       │ metin_temiz     │
│ is_active       │       │ bab             │       │ FULLTEXT INDEX  │
│ created_at      │       │ ravi            │       └─────────────────┘
│ updated_at      │       │ kaynak_link     │
└────────┬────────┘       │ created_at      │       ┌─────────────────┐
         │                 └────────┬────────┘       │ hadis_ingilizce │
         │                          │                ├─────────────────┤
         │                          │◄───────────────│ PK/FK hadis_id  │
         │                          │                │ sanad           │
         │                 ┌────────┴────────┐       │ hadith_detail   │
         │                 │   favoriler     │       │ metin_temiz     │
         │                 ├─────────────────┤       │ FULLTEXT INDEX  │
         │                 │ PK id           │       └─────────────────┘
         │                 │ FK user_id      │
         │                 │ FK hadis_id     │
         │                 │ created_at      │
         │                 │ UK(user,hadis)  │
         │                 └─────────────────┘
         │
         │                 ┌─────────────────┐
         │                 │ refresh_tokens  │
         │                 ├─────────────────┤
         └────────────────►│ FK user_id      │
                           │ PK id           │
                           │ token (unique)  │
                           │ expires_at      │
                           │ created_at      │
                           └─────────────────┘
```

---

## 3. Tablo Şemaları

### 3.1 users

Kullanıcı hesapları ve kimlik doğrulama bilgileri.

```sql
CREATE TABLE users (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    email           VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name       VARCHAR(100),
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Kolonlar:**

| Kolon | Tip | Null | Açıklama |
|-------|-----|------|----------|
| `id` | INT | NO | Primary key, auto increment |
| `email` | VARCHAR(255) | NO | Unique, kullanıcı email adresi |
| `hashed_password` | VARCHAR(255) | NO | bcrypt hashlenmiş şifre |
| `full_name` | VARCHAR(100) | YES | Kullanıcı tam adı |
| `is_active` | BOOLEAN | NO | Hesap aktiflik durumu |
| `created_at` | TIMESTAMP | NO | Kayıt oluşturma zamanı |
| `updated_at` | TIMESTAMP | NO | Son güncelleme zamanı |

**İndeksler:**
- `PRIMARY KEY` (id)
- `UNIQUE KEY` (email)
- `INDEX idx_email` - Login sorguları için

---

### 3.2 hadisler

Hadis metadata bilgileri (kitap, bölüm, ravi).

```sql
CREATE TABLE hadisler (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    hadis_no    VARCHAR(30) NOT NULL,
    kitap       VARCHAR(100) NOT NULL,
    kitap_id    INT,
    bab         TEXT,
    ravi        TEXT,
    kaynak_link VARCHAR(500),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_hadis_no (hadis_no),
    INDEX idx_kitap (kitap),
    INDEX idx_kitap_id (kitap_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Kolonlar:**

| Kolon | Tip | Null | Açıklama |
|-------|-----|------|----------|
| `id` | INT | NO | Primary key |
| `hadis_no` | VARCHAR(30) | NO | Hadis numarası (örn: BH-1, BH-7563) |
| `kitap` | VARCHAR(100) | NO | Kitap adı (örn: Sahih al-Bukhari) |
| `kitap_id` | INT | YES | Kitap ID (bukhari_books.id) |
| `bab` | TEXT | YES | Bölüm/bab adı |
| `ravi` | TEXT | YES | Hadisi rivayet eden sahabeler |
| `kaynak_link` | VARCHAR(500) | YES | sunnah.com linki |
| `created_at` | TIMESTAMP | NO | Kayıt oluşturma zamanı |

**İndeksler:**
- `PRIMARY KEY` (id)
- `INDEX idx_hadis_no` - Hadis numarası arama
- `INDEX idx_kitap` - Kitap bazlı filtreleme
- `INDEX idx_kitap_id` - Kitap ID bazlı join'ler

---

### 3.3 hadis_arapca

Arapça hadis metinleri ve temizlenmiş arama metni.

```sql
CREATE TABLE hadis_arapca (
    hadis_id        INT PRIMARY KEY,
    sanad           MEDIUMTEXT,
    hadith_detail   MEDIUMTEXT NOT NULL,
    metin_temiz     MEDIUMTEXT NOT NULL,
    
    FOREIGN KEY (hadis_id) REFERENCES hadisler(id) ON DELETE CASCADE,
    FULLTEXT INDEX ft_arapca (metin_temiz) WITH PARSER ngram
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Kolonlar:**

| Kolon | Tip | Null | Açıklama |
|-------|-----|------|----------|
| `hadis_id` | INT | NO | FK → hadisler.id, PK |
| `sanad` | MEDIUMTEXT | YES | Rivayet zinciri (orijinal Arapça) |
| `hadith_detail` | MEDIUMTEXT | NO | Hadis metni/matin (orijinal) |
| `metin_temiz` | MEDIUMTEXT | NO | Arama için temizlenmiş metin |

**İndeksler:**
- `PRIMARY KEY` (hadis_id)
- `FULLTEXT INDEX ft_arapca` (metin_temiz) WITH PARSER ngram

**Neden ngram parser?**
- Arapça için karakter tabanlı tokenizasyon
- Varsayılan 2-karakter ngram'lar
- `ft_min_word_len=2` MySQL ayarı

**Temizleme işlemleri (Python'da):**
- Hareke (diakritik işaret) kaldırma
- Elif varyasyonları normalize (ٱإأآا → ا)
- Te/he normalize (ة → ه)
- Noktalama ve özel karakter kaldırma
- Boşluk normalizasyonu

---

### 3.4 hadis_ingilizce

İngilizce hadis metinleri ve temizlenmiş arama metni.

```sql
CREATE TABLE hadis_ingilizce (
    hadis_id        INT PRIMARY KEY,
    sanad           MEDIUMTEXT,
    hadith_detail   MEDIUMTEXT NOT NULL,
    metin_temiz     MEDIUMTEXT NOT NULL,
    
    FOREIGN KEY (hadis_id) REFERENCES hadisler(id) ON DELETE CASCADE,
    FULLTEXT INDEX ft_ingilizce (metin_temiz)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Kolonlar:**

| Kolon | Tip | Null | Açıklama |
|-------|-----|------|----------|
| `hadis_id` | INT | NO | FK → hadisler.id, PK |
| `sanad` | MEDIUMTEXT | YES | Narrator chain (orijinal İngilizce) |
| `hadith_detail` | MEDIUMTEXT | NO | Hadis text (orijinal) |
| `metin_temiz` | MEDIUMTEXT | NO | Arama için temizlenmiş metin |

**İndeksler:**
- `PRIMARY KEY` (hadis_id)
- `FULLTEXT INDEX ft_ingilizce` (metin_temiz)

**Neden standart parser?**
- İngilizce için kelime tabanlı tokenizasyon yeterli
- Stopword kaldırma (a, an, the...)
- Kelime köküne inme (stemming)

**Temizleme işlemleri:**
- Küçük harfe çevirme
- Noktalama kaldırma
- Boşluk normalizasyonu

---

### 3.5 favoriler

Kullanıcı favori hadisleri (many-to-many ilişki).

```sql
CREATE TABLE favoriler (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    user_id     INT NOT NULL,
    hadis_id    INT NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE KEY uk_user_hadis (user_id, hadis_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (hadis_id) REFERENCES hadisler(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_hadis_id (hadis_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Kolonlar:**

| Kolon | Tip | Null | Açıklama |
|-------|-----|------|----------|
| `id` | INT | NO | Primary key |
| `user_id` | INT | NO | FK → users.id |
| `hadis_id` | INT | NO | FK → hadisler.id |
| `created_at` | TIMESTAMP | NO | Favori oluşturma zamanı |

**İndeksler:**
- `PRIMARY KEY` (id)
- `UNIQUE KEY uk_user_hadis` (user_id, hadis_id) - Duplicate önleme
- `INDEX idx_user_id` - Kullanıcının favorilerini listeleme
- `INDEX idx_hadis_id` - Hadis'in favori sayısı

---

### 3.6 refresh_tokens

JWT refresh token saklama.

```sql
CREATE TABLE refresh_tokens (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    user_id     INT NOT NULL,
    token       VARCHAR(512) NOT NULL UNIQUE,
    expires_at  TIMESTAMP NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_token (token(255))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Kolonlar:**

| Kolon | Tip | Null | Açıklama |
|-------|-----|------|----------|
| `id` | INT | NO | Primary key |
| `user_id` | INT | NO | FK → users.id |
| `token` | VARCHAR(512) | NO | JWT refresh token (unique) |
| `expires_at` | TIMESTAMP | NO | Token geçerlilik süresi |
| `created_at` | TIMESTAMP | NO | Token oluşturma zamanı |

**İndeksler:**
- `PRIMARY KEY` (id)
- `UNIQUE KEY` (token)
- `INDEX idx_token` - Token lookup için

---

## 4. İlişkiler (Relationships)

### 4.1 One-to-Many

```
users (1) ────────► (N) refresh_tokens
       Bir kullanıcı birden fazla refresh token sahibi olabilir
       ON DELETE CASCADE: Kullanıcı silinince token'lar da silinir

users (1) ────────► (N) favoriler
       Bir kullanıcı birden fazla hadisi favori yapabilir
       ON DELETE CASCADE: Kullanıcı silinince favoriler de silinir
```

### 4.2 One-to-One

```
hadisler (1) ────────► (1) hadis_arapca
       Her hadisin bir Arapça metni vardır
       ON DELETE CASCADE: Hadis silinince metin de silinir

hadisler (1) ────────► (1) hadis_ingilizce
       Her hadisin bir İngilizce metni vardır
       ON DELETE CASCADE: Hadis silinince metin de silinir
```

### 4.3 Many-to-Many (favoriler üzerinden)

```
users (N) ◄─────► (M) hadisler
       
       Bir kullanıcı çok hadisi favori edebilir
       Bir hadis çok kullanıcı tarafından favori edilebilir
       
       Ara tablo: favoriler
```

---

## 5. FULLTEXT Arama İndeksleri

### 5.1 Arapça İndeks (ngram)

```sql
FULLTEXT INDEX ft_arapca (metin_temiz) WITH PARSER ngram
```

**Ngram parser nasıl çalışır?**
- Varsayılan: 2 karakter ngram'lar
- "الصلاة" → ["ال", "لص", "صل", "لا", "اة"]
- Karakter tabanlı arama sağlar
- Kısa kelimeler için ideal

**MySQL Ayarları:**
```ini
[mysqld]
ngram_token_size=2
ft_min_word_len=2
```

### 5.2 İngilizce İndeks (standart)

```sql
FULLTEXT INDEX ft_ingilizce (metin_temiz)
```

**Standart parser nasıl çalışır?**
- Kelime tabanlı tokenizasyon
- Stopword kaldırma
- Stemming (kelime kökü)
- Uzun metinler için ideal

---

## 6. SQL Sorgu Örnekleri

### 6.1 BM25 Arama (Arapça)

```sql
-- FULLTEXT arama + LIKE boosting
SELECT
    h.id,
    h.hadis_no,
    h.kitap,
    ha.sanad,
    ha.hadith_detail,
    (
        MATCH(ha.metin_temiz) AGAINST(:query IN NATURAL LANGUAGE MODE) * 0.05 +
        CASE WHEN ha.metin_temiz LIKE :term1 THEN 30 ELSE 0 END +
        CASE WHEN ha.metin_temiz LIKE :term2 THEN 24 ELSE 0 END
    ) AS skor
FROM hadisler h
JOIN hadis_arapca ha ON ha.hadis_id = h.id
WHERE ha.metin_temiz LIKE :term1 OR ha.metin_temiz LIKE :term2
ORDER BY skor DESC
LIMIT :limit OFFSET :offset;
```

### 6.2 BM25 Arama (İngilizce)

```sql
SELECT
    h.id,
    h.hadis_no,
    h.kitap,
    hi.sanad,
    hi.hadith_detail,
    MATCH(hi.metin_temiz) AGAINST(:query IN NATURAL LANGUAGE MODE) AS skor
FROM hadisler h
JOIN hadis_ingilizce hi ON hi.hadis_id = h.id
WHERE MATCH(hi.metin_temiz) AGAINST(:query IN NATURAL LANGUAGE MODE) > 0
ORDER BY skor DESC
LIMIT :limit OFFSET :offset;
```

### 6.3 Hadis Detay (Tüm Diller)

```sql
SELECT
    h.id,
    h.hadis_no,
    h.kitap,
    h.bab,
    h.ravi,
    h.kaynak_link,
    ha.sanad AS ar_sanad,
    ha.hadith_detail AS ar_detail,
    hi.sanad AS en_sanad,
    hi.hadith_detail AS en_detail
FROM hadisler h
LEFT JOIN hadis_arapca ha ON ha.hadis_id = h.id
LEFT JOIN hadis_ingilizce hi ON hi.hadis_id = h.id
WHERE h.id = :hadis_id;
```

---

## 7. Veri İçe Aktarma (Import)

### 7.1 CSV'den MySQL'e

```python
# import_data.py akışı:

1. CSV dosyalarını oku (bukhari_arabic.csv, bukhari_english.csv)
2. Her satır için:
   a. hadisler tablosuna metadata ekle
   b. hadis_arapca tablosuna Arapça metin ekle (temizlenmiş)
   c. hadis_ingilizce tablosuna İngilizce metin ekle (temizlenmiş)
3. Commit batch işlemleri
```

### 7.2 Embedding Üretme

```python
# Qdrant'a yükleme akışı:

1. Her hadis için metin_temiz oku
2. sentence-transformers modeli ile embedding üret:
   vector = model.encode(text, normalize_embeddings=True)
3. Qdrant point oluştur:
   {
     "id": hadis_id,
     "vector": vector.tolist(),
     "payload": {"hadis_no": "BH-1", "kitap": "..."}
   }
4. Batch upsert to Qdrant
```

---

## 8. Optimizasyon Stratejileri

### 8.1 Mevcut Optimizasyonlar

1. **Connection Pooling**: SQLAlchemy engine pool_size=10
2. **Async Queries**: asyncmy driver ile non-blocking I/O
3. **FULLTEXT Index**: Hızlı metin arama
4. **Compound Index**: (user_id, hadis_id) unique constraint
5. **Lazy Loading**: İlişkili veriler sadece gerekince çekilir

### 8.2 Gelecek Optimizasyonlar

1. **Read Replicas**: SELECT sorguları için replica DB
2. **Redis Cache**: Sık aranan sorguları önbellekte tutma
3. **Materialized Views**: Karmaşık JOIN'ler için ön hesaplanmış view'lar
4. **Partitioning**: hadisler tablosunu kitap_id ile bölme

---

## 9. Backup ve Recovery

### 9.1 Docker Volume Backup

```bash
# MySQL verisi
docker run --rm -v hadis_mysql_data:/data -v $(pwd):/backup alpine \
    tar czf /backup/mysql_backup.tar.gz -C /data .

# Qdrant verisi
docker run --rm -v hadis_qdrant_data:/data -v $(pwd):/backup alpine \
    tar czf /backup/qdrant_backup.tar.gz -C /data .
```

### 9.2 MySQL Dump

```bash
docker exec hadis_mysql mysqldump -u root -p hadis_db > hadis_db_backup.sql
```

---

## 10. Karakter Seti ve Collation

**Karakter Seti:** `utf8mb4`
- Tüm Unicode karakterleri destekler (emoji dahil)
- Arapça Harfler: U+0600 - U+06FF
- Arapça Ek: U+0750 - U+077F

**Collation:** `utf8mb4_unicode_ci`
- Case-insensitive arama
- Unicode karakter sıralaması
- Arapça için özel sorting kuralları

---

**Versiyon**: 1.0.0
**MySQL Version**: 8.0+
**Son Güncelleme**: Mayıs 2026
