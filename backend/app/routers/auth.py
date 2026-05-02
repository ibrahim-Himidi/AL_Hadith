"""
Auth Router — /auth/register, /auth/login, /auth/refresh, /auth/me
"""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.database.schemas import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserOut,
)
from app.services import auth_service as svc

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()

DbDep = Annotated[AsyncSession, Depends(get_db)]


# ── Kullanıcı doğrulama dependency ───────────────────────────────────────────
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: DbDep,
):
    token = credentials.credentials
    try:
        payload = svc.decode_token(token)
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Geçersiz token türü")
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token geçersiz veya süresi dolmuş",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await svc.get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Kullanıcı bulunamadı")
    return user


CurrentUser = Annotated[object, Depends(get_current_user)]


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(body: RegisterRequest, db: DbDep):
    existing = await svc.get_user_by_email(db, body.email)
    if existing:
        raise HTTPException(status_code=409, detail="Bu e-posta zaten kayıtlı")

    user = await svc.create_user(db, body.email, body.password, body.full_name)
    access_token, expires_in = svc.create_access_token(user.id)
    refresh_token, rt_expires = svc.create_refresh_token(user.id)
    await svc.save_refresh_token(db, user.id, refresh_token, rt_expires)

    return TokenResponse(
        access_token=access_token,
        expires_in=expires_in,
        user=UserOut.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: DbDep):
    user = await svc.get_user_by_email(db, body.email)
    if not user or not svc.verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="E-posta veya şifre hatalı")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Hesap devre dışı")

    access_token, expires_in = svc.create_access_token(user.id)
    refresh_token, rt_expires = svc.create_refresh_token(user.id)
    await svc.save_refresh_token(db, user.id, refresh_token, rt_expires)

    return TokenResponse(
        access_token=access_token,
        expires_in=expires_in,
        user=UserOut.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, db: DbDep):
    try:
        payload = svc.decode_token(body.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Geçersiz refresh token")
        user_id = int(payload["sub"])
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Token geçersiz veya süresi dolmuş")

    rt = await svc.get_refresh_token(db, body.refresh_token)
    if not rt or rt.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token geçersiz")

    await svc.revoke_refresh_token(db, body.refresh_token)

    user = await svc.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Kullanıcı bulunamadı")

    access_token, expires_in = svc.create_access_token(user.id)
    new_refresh, rt_expires = svc.create_refresh_token(user.id)
    await svc.save_refresh_token(db, user.id, new_refresh, rt_expires)

    return TokenResponse(
        access_token=access_token,
        expires_in=expires_in,
        user=UserOut.model_validate(user),
    )


@router.get("/me", response_model=UserOut)
async def me(current_user: CurrentUser):
    return UserOut.model_validate(current_user)
