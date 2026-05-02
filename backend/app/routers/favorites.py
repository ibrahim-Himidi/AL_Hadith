"""
Favoriler Router — CRUD /favoriler (auth gerekli)
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.connection import get_db
from app.database.models import Favori, Hadis, User
from app.database.schemas import FavoriEkleRequest, FavoriListResponse, FavoriOut
from app.routers.auth import get_current_user

router = APIRouter(prefix="/favoriler", tags=["favoriler"])

DbDep          = Annotated[AsyncSession, Depends(get_db)]
CurrentUser    = Annotated[User, Depends(get_current_user)]


@router.get("", response_model=FavoriListResponse)
async def list_favoriler(current_user: CurrentUser, db: DbDep):
    result = await db.execute(
        select(Favori)
        .options(
            selectinload(Favori.hadis).selectinload(Hadis.arapca),
            selectinload(Favori.hadis).selectinload(Hadis.ingilizce),
        )
        .where(Favori.user_id == current_user.id)
        .order_by(Favori.created_at.desc())
    )
    favs = result.scalars().all()
    return FavoriListResponse(
        toplam=len(favs),
        favoriler=[FavoriOut.model_validate(f) for f in favs],
    )


@router.post("", response_model=FavoriOut, status_code=201)
async def ekle_favori(body: FavoriEkleRequest, current_user: CurrentUser, db: DbDep):
    # Hadis var mı?
    hadis = await db.get(Hadis, body.hadis_id)
    if not hadis:
        raise HTTPException(status_code=404, detail="Hadis bulunamadı")

    # Zaten favoride mi?
    existing = await db.execute(
        select(Favori).where(
            Favori.user_id == current_user.id,
            Favori.hadis_id == body.hadis_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Zaten favorilerde")

    fav = Favori(user_id=current_user.id, hadis_id=body.hadis_id)
    db.add(fav)
    await db.flush()
    return FavoriOut.model_validate(fav)


@router.delete("/{hadis_id}", status_code=204)
async def sil_favori(hadis_id: int, current_user: CurrentUser, db: DbDep):
    result = await db.execute(
        select(Favori).where(
            Favori.user_id == current_user.id,
            Favori.hadis_id == hadis_id,
        )
    )
    fav = result.scalar_one_or_none()
    if not fav:
        raise HTTPException(status_code=404, detail="Favori bulunamadı")
    await db.delete(fav)


@router.get("/kontrol/{hadis_id}", response_model=dict)
async def kontrol_favori(hadis_id: int, current_user: CurrentUser, db: DbDep):
    """Belirli bir hadis favoride mi? {favoride: bool}"""
    result = await db.execute(
        select(Favori).where(
            Favori.user_id == current_user.id,
            Favori.hadis_id == hadis_id,
        )
    )
    return {"favoride": result.scalar_one_or_none() is not None}
