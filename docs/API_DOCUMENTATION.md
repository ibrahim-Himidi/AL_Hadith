# API Documentation
## HadithSearch - REST API Referansı

---

## Base URL

```
Geliştirme: http://localhost:8000
Production:   http://api.hadithsearch.com (örnek)
```

---

## Kimlik Doğrulama (Authentication)

API, JWT (JSON Web Token) tabanlı kimlik doğrulama kullanır.

### Token Alınması

Protected endpoint'lere erişmek için önce `/auth/login` veya `/auth/register` 
ile access token alınmalıdır.

### Header Formatı

```http
Authorization: Bearer <access_token>
```

### Token Türleri

| Tür | Süre | Kullanım |
|-----|------|----------|
| Access Token | 60 dakika | API istekleri |
| Refresh Token | 30 gün | Token yenileme |

---

## Endpoint'ler

### Health Check

#### `GET /`
API durumunu kontrol eder.

**Response:**
```json
{
  "status": "ok",
  "service": "Hadis Semantik Arama API",
  "version": "1.0.0"
}
```

#### `GET /health`
Detaylı sağlık kontrolü.

**Response:**
```json
{
  "status": "healthy"
}
```

---

### Arama (Search)

#### `GET /ara`
Hadis arama endpoint'i.

**Query Parameters:**

| Parametre | Tip | Zorunlu | Varsayılan | Açıklama |
|-----------|-----|---------|------------|----------|
| `q` | string | Evet | - | Arama sorgusu |
| `dil` | string | Hayır | `auto` | Dil: `ar`, `en`, veya `auto` |
| `mod` | string | Hayır | `hybrid` | Arama modu: `hybrid`, `vector`, `bm25` |
| `sayfa` | integer | Hayır | `1` | Sayfa numarası (≥1) |
| `limit` | integer | Hayır | `10` | Sayfa başına sonuç (1-50) |

**Örnek İstekler:**

```bash
# Basit İngilizce arama
curl "http://localhost:8000/ara?q=prayer"

# Arapça arama, vektör modu
curl "http://localhost:8000/ara?q=الصلاة&dil=ar&mod=vector"

# Sayfalama ile
curl "http://localhost:8000/ara?q=fasting&sayfa=2&limit=20"

# Sadece BM25 (kelime eşleşmesi)
curl "http://localhost:8000/ara?q=charity&mod=bm25"
```

**Başarılı Response (200):**

```json
{
  "sorgu": "prayer",
  "dil": "en",
  "mod": "hybrid",
  "sayfa": 1,
  "toplam": 156,
  "sonuclar": [
    {
      "id": 123,
      "hadis_no": "BH-456",
      "kitap": "Sahih al-Bukhari",
      "bab": "Book of Prayer",
      "ravi": "Abu Huraira",
      "kaynak_link": "https://sunnah.com/bukhari:456",
      "arapca": {
        "sanad": "حَدَّثَنَا الْحُمَيْدِيُّ...",
        "hadith_detail": "إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ..."
      },
      "ingilizce": {
        "sanad": "Narrated by Al-Humaydi...",
        "hadith_detail": "The deeds are considered by the intentions..."
      },
      "skor": 0.854321
    }
  ]
}
```

**Alan Açıklamaları:**

| Alan | Tip | Açıklama |
|------|-----|----------|
| `sorgu` | string | Orijinal arama sorgusu |
| `dil` | string | Tespit edilen/girilen dil |
| `mod` | string | Kullanılan arama modu |
| `sayfa` | integer | Mevcut sayfa numarası |
| `toplam` | integer | Toplam sonuç sayısı |
| `sonuclar` | array | Hadis sonuçları listesi |
| `sonuclar[].id` | integer | Hadis ID (veritabanı PK) |
| `sonuclar[].hadis_no` | string | Hadis numarası (örn: BH-456) |
| `sonuclar[].kitap` | string | Kitap adı (Sahih al-Bukhari) |
| `sonuclar[].bab` | string | Bölüm/bab adı |
| `sonuclar[].ravi` | string | Ravi (hadisi rivayet eden) |
| `sonuclar[].kaynak_link` | string | sunnah.com linki |
| `sonuclar[].arapca` | object | Arapça metin (sanad + matin) |
| `sonuclar[].ingilizce` | object | İngilizce metin (sanad + text) |
| `sonuclar[].skor` | float | Alaka skoru (0.0 - 1.0+) |

**Hata Response'ları:**

```json
// 400 Bad Request - Eksik parametre
{
  "detail": "Query parameter 'q' is required"
}

// 422 Validation Error
{
  "detail": [
    {
      "loc": ["query", "sayfa"],
      "msg": "ensure this value is greater than or equal to 1",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

---

### Hadis Detay

#### `GET /hadis/{id}`
Tekil hadis detayını getirir.

**Path Parameters:**

| Parametre | Tip | Açıklama |
|-----------|-----|----------|
| `id` | integer | Hadis ID (veritabanı primary key) |

**Örnek İstek:**

```bash
curl "http://localhost:8000/hadis/1"
```

**Başarılı Response (200):**

```json
{
  "id": 1,
  "hadis_no": "BH-1",
  "kitap": "Sahih al-Bukhari",
  "bab": "The Beginning of the Revelation",
  "ravi": "Umar ibn al-Khattab",
  "kaynak_link": "https://sunnah.com/bukhari:1",
  "arapca": {
    "sanad": "حَدَّثَنَا الْحُمَيْدِيُّ عَبْدُ اللَّهِ بْنُ الزُّبَيْرِ...",
    "hadith_detail": "إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ..."
  },
  "ingilizce": {
    "sanad": "Narrated by Al-Humaydi Abdullah bin Al-Zubair...",
    "hadith_detail": "The deeds are considered by the intentions..."
  }
}
```

**Hata Response'ları:**

```json
// 404 Not Found
{
  "detail": "Hadis bulunamadı"
}

// 422 Validation Error
{
  "detail": [
    {
      "loc": ["path", "id"],
      "msg": "value is not a valid integer",
      "type": "type_error.integer"
    }
  ]
}
```

---

### Authentication

#### `POST /auth/register`
Yeni kullanıcı kaydı oluşturur.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "full_name": "John Doe"
}
```

**Alan Validasyonları:**

| Alan | Kurallar |
|------|----------|
| `email` | Geçerli email formatı, unique |
| `password` | Minimum 8 karakter |
| `full_name` | Opsiyonel, max 100 karakter |

**Başarılı Response (201):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true
  }
}
```

**Hata Response'ları:**

```json
// 409 Conflict - Email zaten kayıtlı
{
  "detail": "Bu e-posta zaten kayıtlı"
}

// 422 Validation Error
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "ensure this value has at least 8 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

---

#### `POST /auth/login`
Kullanıcı girişi yapar.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Başarılı Response (200):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true
  }
}
```

**Hata Response'ları:**

```json
// 401 Unauthorized
{
  "detail": "E-posta veya şifre hatalı"
}

// 403 Forbidden - Hesap devre dışı
{
  "detail": "Hesap devre dışı"
}
```

---

#### `POST /auth/refresh`
Access token'ı yeniler.

**Request Body:**

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Başarılı Response (200):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true
  }
}
```

**Not:** Eski refresh token geçersiz olur, yeni token'lar kullanılmalıdır.

**Hata Response'ları:**

```json
// 401 Unauthorized
{
  "detail": "Refresh token geçersiz veya süresi dolmuş"
}
```

---

#### `GET /auth/me`
Mevcut kullanıcı bilgilerini döner. (Protected)

**Headers:**

```http
Authorization: Bearer <access_token>
```

**Başarılı Response (200):**

```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true
}
```

**Hata Response'ları:**

```json
// 401 Unauthorized - Token yok/invalid
{
  "detail": "Token geçersiz veya süresi dolmuş"
}
```

---

## Hata Kodları

| HTTP Code | Açıklama |
|-----------|----------|
| 200 OK | İstek başarılı |
| 201 Created | Kaynak oluşturuldu (register) |
| 400 Bad Request | Geçersiz istek formatı |
| 401 Unauthorized | Kimlik doğrulama gerekli/geçersiz |
| 403 Forbidden | Yetki yetersiz |
| 404 Not Found | Kaynak bulunamadı |
| 409 Conflict | Çakışma (duplicate email) |
| 422 Unprocessable Entity | Validasyon hatası |
| 500 Internal Server Error | Sunucu hatası |

---

## Örnek Kullanım Senaryoları

### Senaryo 1: Basit Arama

```bash
# İngilizce arama
curl "http://localhost:8000/ara?q=prayer"

# Arapça arama  
curl "http://localhost:8000/ara?q=الصلاة"
```

### Senaryo 2: Sayfalama ile Arama

```bash
# İlk sayfa (varsayılan)
curl "http://localhost:8000/ara?q=fasting&limit=10"

# İkinci sayfa
curl "http://localhost:8000/ara?q=fasting&sayfa=2&limit=10"

# Tüm sonuçları gör (max 50)
curl "http://localhost:8000/ara?q=fasting&limit=50"
```

### Senaryo 3: Farklı Arama Modları

```bash
# Hibrit (varsayılan) - en iyi sonuçlar
curl "http://localhost:8000/ara?q=charity&mod=hybrid"

# Sadece vektör - anlam benzerliği odaklı
curl "http://localhost:8000/ara?q=generosity&mod=vector"

# Sadece BM25 - kelime eşleşmesi odaklı
curl "http://localhost:8000/ara?q=zakat&mod=bm25"
```

### Senaryo 4: Kimlik Doğrulama Akışı

```bash
# 1. Kayıt ol veya giriş yap
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass123"}'

# 2. Response'dan access_token'ı al ve sonraki isteklerde kullan
# Authorization: Bearer <token>

# 3. Mevcut kullanıcı bilgilerini al
curl "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."

# 4. Token süresi dolunca yenile
curl -X POST "http://localhost:8000/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"eyJhbGciOiJIUzI1NiIs..."}'
```

---

## Rate Limiting

Mevcut sürümde rate limiting uygulanmamıştır. Gelecek sürümlerde eklenecektir.

Önerilen limitler:
- Arama: 100 req/min per IP
- Auth: 10 req/min per IP

---

## CORS Politikası

API aşağıdaki origin'lere izin verir:
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (Alternatif dev server)

Production ortamında bu liste yapılandırılabilir.

---

## OpenAPI / Swagger

API otomatik olarak OpenAPI şeması üretir:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

---

**Versiyon**: 1.0.0
**Son Güncelleme**: Mayıs 2026
