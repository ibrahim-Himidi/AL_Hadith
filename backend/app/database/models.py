"""
SQLAlchemy ORM Modelleri
========================
Tablolar: users, hadisler, hadis_arapca, hadis_ingilizce, favoriler, refresh_tokens
"""

from datetime import datetime

from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Index, Integer,
    String, Text, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


# ─────────────────────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id:              Mapped[int]      = mapped_column(Integer, primary_key=True, autoincrement=True)
    email:           Mapped[str]      = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str]      = mapped_column(String(255), nullable=False)
    full_name:       Mapped[str|None] = mapped_column(String(100))
    is_active:       Mapped[bool]     = mapped_column(Boolean, default=True)
    created_at:      Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at:      Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # İlişkiler
    favoriler:       Mapped[list["Favori"]]       = relationship("Favori", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens:  Mapped[list["RefreshToken"]] = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")


# ─────────────────────────────────────────────────────────────────────────────
class Hadis(Base):
    __tablename__ = "hadisler"

    id:          Mapped[int]      = mapped_column(Integer, primary_key=True, autoincrement=True)
    hadis_no:    Mapped[str]      = mapped_column(String(30), nullable=False)
    kitap:       Mapped[str]      = mapped_column(String(100), nullable=False)
    kitap_id:    Mapped[int|None] = mapped_column(Integer)
    bab:         Mapped[str|None] = mapped_column(Text)
    ravi:        Mapped[str|None] = mapped_column(Text)
    kaynak_link: Mapped[str|None] = mapped_column(String(500))
    created_at:  Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # İlişkiler
    arapca:    Mapped["HadisArapca|None"]    = relationship("HadisArapca", back_populates="hadis", uselist=False, cascade="all, delete-orphan")
    ingilizce: Mapped["HadisIngilizce|None"] = relationship("HadisIngilizce", back_populates="hadis", uselist=False, cascade="all, delete-orphan")
    favoriler: Mapped[list["Favori"]]         = relationship("Favori", back_populates="hadis", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_hadis_no", "hadis_no"),
        Index("idx_kitap_id", "kitap_id"),
    )


# ─────────────────────────────────────────────────────────────────────────────
class HadisArapca(Base):
    __tablename__ = "hadis_arapca"

    hadis_id:     Mapped[int]      = mapped_column(Integer, ForeignKey("hadisler.id", ondelete="CASCADE"), primary_key=True)
    sanad:        Mapped[str|None] = mapped_column(Text)
    hadith_detail:Mapped[str]      = mapped_column(Text, nullable=False)
    metin_temiz:  Mapped[str]      = mapped_column(Text, nullable=False)

    hadis: Mapped["Hadis"] = relationship("Hadis", back_populates="arapca")


# ─────────────────────────────────────────────────────────────────────────────
class HadisIngilizce(Base):
    __tablename__ = "hadis_ingilizce"

    hadis_id:     Mapped[int]      = mapped_column(Integer, ForeignKey("hadisler.id", ondelete="CASCADE"), primary_key=True)
    sanad:        Mapped[str|None] = mapped_column(Text)
    hadith_detail:Mapped[str]      = mapped_column(Text, nullable=False)
    metin_temiz:  Mapped[str]      = mapped_column(Text, nullable=False)

    hadis: Mapped["Hadis"] = relationship("Hadis", back_populates="ingilizce")


# ─────────────────────────────────────────────────────────────────────────────
class Favori(Base):
    __tablename__ = "favoriler"

    id:         Mapped[int]      = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id:    Mapped[int]      = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    hadis_id:   Mapped[int]      = mapped_column(Integer, ForeignKey("hadisler.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user:  Mapped["User"]  = relationship("User",  back_populates="favoriler")
    hadis: Mapped["Hadis"] = relationship("Hadis", back_populates="favoriler")

    __table_args__ = (
        Index("uk_user_hadis", "user_id", "hadis_id", unique=True),
    )


# ─────────────────────────────────────────────────────────────────────────────
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id:         Mapped[int]      = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id:    Mapped[int]      = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token:      Mapped[str]      = mapped_column(String(512), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")
