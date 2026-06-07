from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.attention_event import AttentionEvent
from app.db.models.app_activity import AppActivity
from app.db.models.focus_score import FocusScore
from app.db.models.session import Session as SessionModel
from app.repositories.session_repo import SessionRepository


class SessionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.sessions = SessionRepository(db)

    def start_session(self, user_id: UUID, label: str | None) -> SessionModel:
        session_obj = SessionModel(user_id=str(user_id), label=label)
        self.sessions.add(session_obj)
        self.db.commit()
        self.db.refresh(session_obj)
        return session_obj

    def stop_session(self, session_id: UUID) -> SessionModel:
        session_obj = self.db.get(SessionModel, str(session_id))
        if session_obj is None:
            raise ValueError("Session not found")
        average_score = self._average_focus_for_session(str(session_id))
        session_obj.end_time = datetime.now(timezone.utc)
        session_obj.overall_score = average_score
        self.db.commit()
        self.db.refresh(session_obj)
        return session_obj

    def list_sessions(self, user_id: UUID) -> list[SessionModel]:
        return self.sessions.list_for_user(str(user_id))

    def get_session(self, session_id: UUID) -> SessionModel:
        session_obj = self.db.get(SessionModel, str(session_id))
        if session_obj is None:
            raise ValueError("Session not found")
        return session_obj

    def summary(self, session_id: UUID) -> dict[str, object]:
        session_obj = self.get_session(session_id)
        focus_samples = self.db.query(func.count(FocusScore.score_id)).filter(FocusScore.session_id == str(session_id)).scalar() or 0
        app_count = self.db.query(func.count(AppActivity.activity_id)).filter(AppActivity.session_id == str(session_id)).scalar() or 0
        drift_count = (
            self.db.query(func.count(AttentionEvent.event_id))
            .filter(AttentionEvent.session_id == str(session_id))
            .scalar()
            or 0
        )
        duration_minutes = 0.0
        if session_obj.end_time:
            duration_minutes = (session_obj.end_time - session_obj.start_time).total_seconds() / 60.0
        return {
            "session_id": session_obj.session_id,
            "label": session_obj.label,
            "average_focus": float(session_obj.overall_score or 0.0),
            "drift_count": drift_count,
            "app_count": app_count,
            "focus_samples": focus_samples,
            "duration_minutes": duration_minutes,
        }

    def _average_focus_for_session(self, session_id: str) -> float:
        statement = select(func.avg(FocusScore.score)).where(FocusScore.session_id == session_id)
        average = self.db.execute(statement).scalar_one_or_none()
        return float(average or 0.0)
