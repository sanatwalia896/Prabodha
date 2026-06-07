from fastapi import APIRouter, Depends, status

from app.api.deps import db_session
from app.core.config import get_settings
from app.schemas.auth import TokenResponse, UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db=Depends(db_session)) -> UserResponse:
    user = AuthService(db, get_settings()).register(payload.username, payload.password)
    return UserResponse(user_id=user.user_id, username=user.username, settings=user.settings, created_at=user.created_at.isoformat())


@router.post("/login", response_model=TokenResponse)
def login_user(payload: UserLogin, db=Depends(db_session)) -> TokenResponse:
    token = AuthService(db, get_settings()).login(payload.username, payload.password)
    return TokenResponse(access_token=token, token_type="bearer")
