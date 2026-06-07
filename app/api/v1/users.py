from fastapi import APIRouter, Depends

from app.api.deps import current_user, db_session
from app.schemas.auth import UserResponse, UserSettingsUpdate
from app.services.auth_service import AuthService
from app.core.config import get_settings

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def read_me(user=Depends(current_user)) -> UserResponse:
    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        settings=user.settings,
        created_at=user.created_at.isoformat(),
    )


@router.patch("/settings", response_model=UserResponse)
def update_settings(payload: UserSettingsUpdate, user=Depends(current_user), db=Depends(db_session)) -> UserResponse:
    service = AuthService(db, get_settings())
    updated = service.update_settings(user_id=user.user_id, settings_update=payload.settings)
    return UserResponse(
        user_id=updated.user_id,
        username=updated.username,
        settings=updated.settings,
        created_at=updated.created_at.isoformat(),
    )
