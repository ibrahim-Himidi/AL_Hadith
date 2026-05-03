# System Architecture Documentation
## HadithSearch - Sistem Mimarisi Dokümantasyonu

---

## 1. Genel Bakış

HadithSearch, 3 katmanlı bir mimari kullanır:
- **Presentation Layer**: Vue.js 3 Frontend
- **Application Layer**: FastAPI Backend  
- **Data Layer**: MySQL + Qdrant Veritabanları

---

## 2. Bileşen Diyagramı

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Vue.js 3 Frontend                           │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │   │
│  │  │  App.vue    │  │ HadithCard  │  │ SearchBox   │  │  Auth UI  │ │   │
│  │  │ (Ana App)   │  │ (Kart)      │  │ (Arama)     │  │ (Login)   │ │   │
│  │  └──────┬──────┘  └─────────────┘  └─────────────┘  └───────────┘ │   │
│  │         │                                                          │   │
│  │         │ HTTP/REST API                                            │   │
│  │         ▼                                                          │   │
│  │  ┌─────────────────────────────────────────────────────────────┐  │   │
│  │  │                 Axios / Fetch Client                         │  │   │
│  │  │         Base URL: http://localhost:8000                    │  │   │
│  │  └─────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────┬─────────────────────────────────────┘
                                      │ HTTP/JSON
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          APPLICATION LAYER                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      FastAPI Backend                               │   │
│  │                                                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐  │   │
│  │  │                     API Routers                              │  │   │
│  │  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐  │  │   │
│  │  │  │ /ara         │ │ /auth/*      │ │ /hadis/{id}          │  │  │   │
│  │  │  │ SearchRouter │ │ AuthRouter   │ │ HadithRouter         │  │  │   │
│  │  │  │ GET /ara     │ │ POST /login  │ │ GET /hadis/{id}      │  │  │   │
│  │  │  └──────┬───────┘ └──────┬───────┘ └──────────┬───────────┘  │  │   │
│  │  │         └─────────────────┴──────────────────┘              │  │   │
│  │  │                           │                                │  │   │
│  │  │                           ▼                                │  │   │
│  │  │  ┌─────────────────────────────────────────────────────────┐│  │   │
│  │  │  │                    Service Layer                       ││  │   │
│  │  │  │  ┌─────────────────┐ ┌─────────────────┐ ┌──────────┐ ││  │   │
│  │  │  │  │ HybridService   │ │ BM25Service     │ │ Vector   │ ││  │   │
│  │  │  │  │                 │ │                 │ │ Service  │ ││  │   │
│  │  │  │  │ - RRF Fusion    │ │ - MySQL FULLTEXT│ │ - Qdrant │ ││  │   │
│  │  │  │  │ - Result Merge  │ │ - Like Boost    │ │ - Embed  │ ││  │   │
│  │  │  │  └─────────────────┘ └─────────────────┘ └──────────┘ ││  │   │
│  │  │  └─────────────────────────────────────────────────────────┘│  │   │
│  │  │                           │                                │  │   │
│  │  │                           ▼                                │  │   │
│  │  │  ┌─────────────────────────────────────────────────────────┐│  │   │
│  │  │  │                    Auth Services                       ││  │   │
│  │  │  │  ┌─────────────────┐ ┌─────────────────┐               ││  │   │
│  │  │  │  │ AuthService     │ │ JWT Handler     │               ││  │   │
│  │  │  │  │ - Password Hash │ │ - Token Gen     │               ││  │   │
│  │  │  │  │ - User CRUD     │ │ - Token Valid   │               ││  │   │
│  │  │  │  └─────────────────┘ └─────────────────┘               ││  │   │
│  │  │  └─────────────────────────────────────────────────────────┘│  │   │
│  │  └─────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────┬─────────────────────────────────────┘
                      ┌───────────────┴───────────────┐
                      │                               │
                      ▼                               ▼
┌─────────────────────────────────┐ ┌─────────────────────────────────────────┐
│        RELATIONAL DB            │ │           VECTOR DB                     │
│  ┌─────────────────────────┐   │ │  ┌─────────────────────────────────────┐│
│  │      MySQL 8.0          │   │ │  │          Qdrant                     ││
│  │  ┌─────────────────┐   │   │ │  │  ┌─────────────────────────────┐   ││
│  │  │ SQLAlchemy ORM  │   │   │ │  │  │ Collection: hadisler_ar     │   ││
│  │  │  (asyncmy)      │   │   │ │  │  │ Collection: hadisler_en     │   ││
│  │  └────────┬────────┘   │   │ │  │  │                             │   ││
│  │           │            │   │ │  │  │ Points: 7,277 per lang    │   ││
│  │           ▼            │   │ │  │  │ Dimension: 768            │   ││
│  │  ┌─────────────────┐   │   │ │  │  │ Distance: Cosine          │   ││
│  │  │ hadisler        │   │   │ │  │  │ HNSW Index                │   ││
│  │  │ hadis_arapca    │◄──┼───┼─┘  │  └─────────────────────────────┘   ││
│  │  │ hadis_ingilizce │◄──┘   │    └─────────────────────────────────────┘
│  │  │ users           │       │
│  │  │ refresh_tokens  │       │
│  │  └─────────────────┘       │
│  └────────────────────────────┘
└─────────────────────────────────┘
```

---

## 3. Veri Akışı (Data Flow)

### 3.1 Arama Akışı

```
Kullanıcı
   │
   │ 1. Arama sorgusu girer
   ▼
┌────────────────┐
│  Vue Frontend  │
│  (App.vue)     │
└───────┬────────┘
        │ 2. HTTP GET /ara?q=...&mod=hybrid
        ▼
┌────────────────┐
│  FastAPI       │
│  SearchRouter  │
└───────┬────────┘
        │ 3. Dil algılama (detect_language)
        │ 4. search_mode kontrolü
        ▼
   ┌────┴────┐
   │         │
   ▼         ▼
┌───────┐ ┌───────┐
│ BM25  │ │ Vektör│  5. Paralel sorgu
│ Svc   │ │ Svc   │
└───┬───┘ └───┬───┘
    │         │
    │ 6. Sonuçlar
    ▼         ▼
┌────────────────┐
│ RRF Fusion     │  7. Reciprocal Rank Fusion
│ (k=60)         │     scores = 1/(k+rank)
└───────┬────────┘
        │ 8. Birleştirilmiş sonuçlar
        ▼
┌────────────────┐
│ Fetch Details  │  9. MySQL'den detay çek
│ (MySQL)        │
└───────┬────────┘
        │ 10. JSON Response
        ▼
┌────────────────┐
│  Vue Frontend  │  11. Sonuçları render et
│  (HadithCard)  │
└────────────────┘
```

### 3.2 Authentication Akışı

```
Kullanıcı
   │
   │ Register/Login
   ▼
Frontend
   │
   │ POST /auth/register veya /auth/login
   ▼
AuthRouter
   │
   │ bcrypt password hash
   ▼
AuthService
   │
   │ JWT Token oluştur
   ▼
┌─────────────┐    ┌─────────────┐
│ Access Token│    │Refresh Token│
│ (60 dk)     │    │ (30 gün)    │
└─────────────┘    └─────────────┘
   │                    │
   │ Frontend'de sakla  │ MySQL refresh_tokens tablosuna kaydet
   ▼                    ▼
Client Storage      Database
```

---

## 4. Servis Katmanı Detayı

### 4.1 HybridService

```python
async def hybrid_search(
    query: str,
    dil: str = "auto",
    sayfa: int = 1,
    limit: int = 10,
    search_mode: str = "hybrid"
) → tuple[list[dict], int, str]
```

**Akış:**
1. Dil tespiti (auto → ar/en)
2. Qdrant hazır mı kontrolü
3. Eğer hazır değilse veya bm25 modu → sadece BM25
4. Eğer vector modu → sadece Qdrant
5. Hybrid mod → Paralel BM25 + Vektör
6. RRF Fusion ile birleştir
7. Sayfalama ve detay çekme

### 4.2 BM25Service

**Arapça Arama:**
- `normalize_arabic_query()`: Hareke kaldırma, elif normalize
- `build_arabic_terms()`: LIKE pattern oluşturma
- SQL: `MATCH(...) AGAINST(...)` + LIKE boosting

**İngilizce Arama:**
- Direkt MySQL FULLTEXT NATURAL LANGUAGE MODE
- Basit kelime eşleşmesi

### 4.3 VectorService

**Embedding:**
- Model: `paraphrase-multilingual-mpnet-base-v2`
- Boyut: 768
- Normalize: Evet (cosine similarity için)

**Qdrant Sorgu:**
- Collection: `hadisler_ar` veya `hadisler_en`
- Algorithm: HNSW
- Distance: Cosine

---

## 5. Veritabanı Erişim Katmanı

### 5.1 SQLAlchemy ORM Yapısı

```
Base (declarative_base)
   │
   ├── User
   │   ├── id, email, hashed_password, full_name
   │   ├── is_active, created_at, updated_at
   │   └── relationships: favoriler[], refresh_tokens[]
   │
   ├── Hadis
   │   ├── id, hadis_no, kitap, kitap_id, bab, ravi
   │   ├── kaynak_link, created_at
   │   └── relationships: arapca, ingilizce, favoriler[]
   │
   ├── HadisArapca
   │   ├── hadis_id (PK, FK), sanad, hadith_detail
   │   └── metin_temiz (FULLTEXT indexed)
   │
   ├── HadisIngilizce
   │   ├── hadis_id (PK, FK), sanad, hadith_detail
   │   └── metin_temiz (FULLTEXT indexed)
   │
   └── RefreshToken
       ├── id, user_id (FK), token, expires_at
       └── created_at
```

### 5.2 Bağlantı Yönetimi

```python
# Async engine oluşturma
engine = create_async_engine(
    "mysql+asyncmy://...",
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
```

---

## 6. Güvenlik Katmanı

### 6.1 CORS Yapılandırması

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 6.2 JWT Authentication

```
Request
   │
   │ Authorization: Bearer <token>
   ▼
HTTPBearer (FastAPI security)
   │
   ▼
jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
   │
   ▼
Token valid? → User ID extract
   │
   ▼
DB'den kullanıcı bilgisi çek
   │
   ▼
Endpoint handler'a inject et
```

---

## 7. Docker Mimarisi

### 7.1 Container İlişkileri

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Compose                       │
│                                                         │
│  ┌─────────────┐     ┌─────────────┐     ┌──────────┐ │
│  │   MySQL     │◄────│   Backend   │────►│  Qdrant  │ │
│  │   :3306     │       :8000         │   │  :6333   │ │
│  └─────────────┘     └─────────────┘     └──────────┘ │
│         ▲                                            │
│         │                                            │
│    [init.sql mount]                                  │
│    [mysql_data vol]                                  │
│                                                      │
└─────────────────────────────────────────────────────────┘
```

### 7.2 Network Akışı

```
Host Machine
   │
   ├──► Port 5173 → Frontend Dev Server (Vite)
   │
   ├──► Port 8000 → FastAPI Backend
   │
   ├──► Port 3306 → MySQL
   │
   └──► Port 6333 → Qdrant Dashboard
```

---

## 8. Ölçeklenebilirlik Stratejisi

### 8.1 Yatay Ölçekleme

```
                      ┌─────────────┐
                      │   Nginx     │
                      │  (Load Bal) │
                      └──────┬──────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌─────────┐    ┌─────────┐    ┌─────────┐
        │Backend 1│    │Backend 2│    │Backend 3│
        │ :8000   │    │ :8001   │    │ :8002   │
        └────┬────┘    └────┬────┘    └────┬────┘
             │              │              │
             └──────────────┼──────────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
        ┌─────────┐   ┌─────────┐   ┌─────────┐
        │  MySQL  │   │  Qdrant │   │  Redis  │
        │ Primary │   │ Cluster │   │  Cache  │
        └─────────┘   └─────────┘   └─────────┘
```

### 8.2 Performans Optimizasyonları

Mevcut:
- Connection pooling (SQLAlchemy)
- Lazy model loading (sentence-transformers)
- Async database queries
- Paralel BM25 + Vector sorguları

Gelecek:
- Redis result caching
- CDN for static assets
- Database read replicas

---

## 9. Hata Yönetimi

### 9.1 Exception Hierarchy

```
Exception
   │
   ├── HTTPException (FastAPI)
   │   ├── 400: Bad Request (validation error)
   │   ├── 401: Unauthorized (auth error)
   │   ├── 404: Not Found
   │   └── 500: Internal Server Error
   │
   └── Custom Exceptions
       ├── QdrantConnectionError
       ├── DatabaseConnectionError
       └── AuthenticationError
```

### 9.2 Hata Akışı

```
Endpoint
   │
   │ try:
   │   await service.call()
   │ except Exception as e:
   ▼
Exception Handler
   │
   ├── Log error details
   │
   └── Return JSONResponse
       {
         "error": "...",
         "detail": "..."
       }
```

---

## 10. Monitoring ve Logging

### 10.1 Log Yapısı

```python
# Startup log
print("🚀 Hadis API başlatılıyor...")

# Shutdown log
print("⛔ Hadis API kapatılıyor...")

# Request logging (Uvicorn default)
INFO:     127.0.0.1:12345 - "GET /ara?q=prayer HTTP/1.1" 200 OK
```

### 10.2 Health Checks

```
GET /health → {"status": "healthy"}
GET /       → {"status": "ok", "service": "...", "version": "1.0.0"}
```

---

## 11. Mimari Kararları

### 11.1 Neden FastAPI?
- ✅ Async desteği
- ✅ Otomatik OpenAPI/Swagger
- ✅ Pydantic validasyonu
- ✅ Dependency injection
- ✅ Type hints zorunluluğu

### 11.2 Neden Qdrant?
- ✅ Açık kaynak
- ✅ HNSW indeksi (hızlı arama)
- ✅ REST API
- ✅ Docker deployment kolaylığı
- ✅ Python client (qdrant-client)

### 11.3 Neden Hybrid Search?
- ✅ BM25: Tam eşleşme garantisi
- ✅ Vector: Anlamsal benzerlik
- ✅ RRF: İkisinin en iyisi

### 11.4 Neden Ayrı Tablolar (ar/en)?
- ✅ FULLTEXT index optimizasyonu
- ✅ Dil bazlı sorgu kolaylığı
- ✅ Bağımsız embedding koleksiyonları

---

## 12. Referanslar

- FastAPI Architecture: https://fastapi.tiangolo.com/
- Qdrant Architecture: https://qdrant.tech/documentation/
- Vue.js Composition API: https://vuejs.org/guide/
- SQLAlchemy Async: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html

---

**Son Güncelleme**: Mayıs 2026
**Versiyon**: 1.0.0
