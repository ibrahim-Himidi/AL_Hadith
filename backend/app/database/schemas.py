"""
Pydantic Şemaları (Request / Response modelleri)
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


# ─────────────────────────────────────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email:     EmailStr
    password:  str = Field(min_length=8, max_length=100)
    full_name: str | None = Field(default=None, max_length=100)


class LoginRequest(BaseModel):
    email:    EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token:  str
    token_type:    str = "bearer"
    expires_in:    int          # saniye cinsinden
    user:          "UserOut"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    id:         int
    email:      str
    full_name:  str | None
    is_active:  bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────────────────────
# Hadis
# ─────────────────────────────────────────────────────────────────────────────

class ArapcaOut(BaseModel):
    sanad:         str | None
    hadith_detail: str

    model_config = {"from_attributes": True}


class IngilizceOut(BaseModel):
    sanad:         str | None
    hadith_detail: str

    model_config = {"from_attributes": True}


class HadisOut(BaseModel):
    id:          int
    hadis_no:    str
    kitap:       str
    bab:         str | None
    ravi:        str | None
    kaynak_link: str | None
    arapca:      ArapcaOut | None
    ingilizce:   IngilizceOut | None
    skor:        float | None = None      # Arama skoru (opsiyonel)

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────────────────────────────────────
# Arama
# ─────────────────────────────────────────────────────────────────────────────

class SearchResponse(BaseModel):
    sorgu:    str
    dil:      str                  # "ar" | "en" | "auto"
    mod:      str = "bm25_only"   # "hybrid" | "bm25_only"
    sayfa:    int
    toplam:   int
    sonuclar: list[HadisOut]


# ─────────────────────────────────────────────────────────────────────────────
# Favoriler
# ─────────────────────────────────────────────────────────────────────────────

class FavoriOut(BaseModel):
    id:         int
    hadis_id:   int
    created_at: datetime
    hadis:      HadisOut | None = None

    model_config = {"from_attributes": True}


class FavoriEkleRequest(BaseModel):
    hadis_id: int


class FavoriListResponse(BaseModel):
    toplam:   int
    favoriler: list[FavoriOut]
