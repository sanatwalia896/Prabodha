from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.session import Session as SessionModel
from app.repositories.base_repo import BaseRepository


class SessionRepository(BaseRepository[SessionModel]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, SessionModel)

    def list_for_user(self, user_id: str) -> list[SessionModel]:
        statement = select(SessionModel).where(SessionModel.user_id == user_id).order_by(SessionModel.start_time.desc())
        return list(self.db.execute(statement).scalars().all())

    def close_session(self, session_id: str, ended_at: datetime, overall_score: float | None) -> SessionModel | None:
        session_obj = self.get(session_id)
        if session_obj is None:
            return None
        session_obj.end_time = ended_at
        session_obj.overall_score = overall_score
        self.db.flush()
        return session_obj
