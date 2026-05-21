from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from app.api.deps import DB
from app.schemas.auth import (
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.services import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(db: DB, payload: RegisterRequest) -> TokenResponse:
    service = AuthService(db)
    return await service.register(
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
    )


@router.post("/token", response_model=TokenResponse)
async def login(
    db: DB,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> TokenResponse:
    service = AuthService(db)
    return await service.authenticate(
        email=form_data.username,
        password=form_data.password,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(db: DB, payload: RefreshRequest) -> TokenResponse:
    service = AuthService(db)
    return await service.refresh(refresh_token=payload.refresh_token)
