from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.app_activity import AppActivity
from app.db.models.attention_event import AttentionEvent
from app.db.models.enums import AttentionEventType, FocusLevel
from app.db.models.focus_score import FocusScore
from app.repositories.event_repo import AppActivityRepository, AttentionEventRepository, FocusScoreRepository


class EventService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.attention_events = AttentionEventRepository(db)
        self.activities = AppActivityRepository(db)
        self.scores = FocusScoreRepository(db)

    def log_attention(self, session_id: UUID, event_type: str, confidence: float, metadata: dict[str, object]) -> AttentionEvent:
        event = self.attention_events.create_attention_event(
            session_id=str(session_id),
            event_type=AttentionEventType(event_type),
            confidence=confidence,
            metadata=metadata,
            timestamp=datetime.now(timezone.utc),
        )
        self.db.commit()
        self.db.refresh(event)
        return event

    def log_activity(
        self,
        session_id: UUID,
        app_name: str,
        window_title: str | None,
        duration_seconds: int | None,
    ) -> AppActivity:
        activity = self.activities.create_activity(
            session_id=str(session_id),
            app_name=app_name,
            window_title=window_title,
            duration_seconds=duration_seconds,
            timestamp=datetime.now(timezone.utc),
        )
        self.db.commit()
        self.db.refresh(activity)
        return activity

    def log_score(self, session_id: UUID, score: float, level: str) -> FocusScore:
        score_obj = self.scores.create_score(
            session_id=str(session_id),
            score=score,
            level=FocusLevel(level),
            timestamp=datetime.now(timezone.utc),
        )
        self.db.commit()
        self.db.refresh(score_obj)
        return score_obj
