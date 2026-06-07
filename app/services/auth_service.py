from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.security import create_access_token, hash_password, verify_password
from app.db.models.user import User
from app.repositories.user_repo import UserRepository


class AuthenticationError(RuntimeError):
    pass


class AuthService:
    def __init__(self, db: Session, settings: Settings) -> None:
        self.db = db
        self.settings = settings
        self.users = UserRepository(db)

    def register(self, username: str, password: str) -> User:
        if self.users.get_by_username(username) is not None:
            raise ValueError("Username already exists")
        user = User(username=username, password_hash=hash_password(password), settings={})
        self.users.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def login(self, username: str, password: str) -> str:
        user = self.users.get_by_username(username)
        if user is None or not verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid credentials")
        return create_access_token(str(user.user_id), self.settings.jwt_secret, self.settings.access_token_minutes)

    def update_settings(self, user_id: UUID, settings_update: dict[str, object]) -> User:
        user = self.db.get(User, str(user_id))
        if user is None:
            raise ValueError("User not found")
        user.settings = settings_update
        self.db.commit()
        self.db.refresh(user)
        return user
