"""
FastAPI Ana Uygulama
====================
Hadis Semantik Arama Sistemi — Backend API
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import auth, favorites, hadith, search


# ── Lifecycle ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Hadis API başlatılıyor...")
    yield
    # Shutdown
    print("⛔ Hadis API kapatılıyor...")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Hadis Semantik Arama API",
    description="""
## Sahih Bukhari Arama Sistemi

Arapça ve İngilizce hadisleri semantik olarak arayan REST API.

### Özellikler
- **BM25 Arama**: MySQL FULLTEXT ile hızlı kelime araması
- **Semantik Arama** *(Faz 2)*: Sentence Transformers + Qdrant
- **Hibrit Arama** *(Faz 2)*: RRF Fusion
- **JWT Auth**: Kullanıcı kaydı, giriş ve favoriler
- **Çok Dilli**: Arapça (RTL) + İngilizce otomatik algılama
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(search.router)
app.include_router(hadith.router)
app.include_router(favorites.router)


# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/", tags=["health"])
async def root():
    return {"status": "ok", "service": "Hadis Semantik Arama API", "version": "1.0.0"}


@app.get("/health", tags=["health"])
async def health():
    return JSONResponse({"status": "healthy"})
