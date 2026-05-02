"""
Hadis Router — GET /hadis/{id}
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.connection import get_db
from app.database.models import Hadis
from app.database.schemas import HadisOut

router = APIRouter(prefix="/hadis", tags=["hadis"])

DbDep = Annotated[AsyncSession, Depends(get_db)]


@router.get("/{hadis_id}", response_model=HadisOut)
async def get_hadis(hadis_id: int, db: DbDep):
    result = await db.execute(
        select(Hadis)
        .options(
            selectinload(Hadis.arapca),
            selectinload(Hadis.ingilizce),
        )
        .where(Hadis.id == hadis_id)
    )
    hadis = result.scalar_one_or_none()
    if not hadis:
        raise HTTPException(status_code=404, detail=f"Hadis bulunamadı: {hadis_id}")
    return HadisOut.model_validate(hadis)


@router.get("/no/{hadis_no}", response_model=HadisOut)
async def get_hadis_by_no(hadis_no: str, db: DbDep):
    """BH-1 gibi hadis numarası ile sorgula."""
    result = await db.execute(
        select(Hadis)
        .options(
            selectinload(Hadis.arapca),
            selectinload(Hadis.ingilizce),
        )
        .where(Hadis.hadis_no == hadis_no.upper())
    )
    hadis = result.scalar_one_or_none()
    if not hadis:
        raise HTTPException(status_code=404, detail=f"Hadis bulunamadı: {hadis_no}")
    return HadisOut.model_validate(hadis)
