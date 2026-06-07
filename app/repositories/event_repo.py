from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models.app_activity import AppActivity
from app.db.models.attention_event import AttentionEvent
from app.db.models.enums import AttentionEventType, FocusLevel
from app.db.models.focus_score import FocusScore
from app.repositories.base_repo import BaseRepository


class AttentionEventRepository(BaseRepository[AttentionEvent]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, AttentionEvent)

    def create_attention_event(
        self,
        session_id: str,
        event_type: AttentionEventType,
        confidence: float,
        metadata: dict,
        timestamp: datetime,
    ) -> AttentionEvent:
        event = AttentionEvent(
            session_id=session_id,
            event_type=event_type,
            confidence=confidence,
            event_metadata=metadata,
            timestamp=timestamp,
        )
        return self.add(event)


class AppActivityRepository(BaseRepository[AppActivity]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, AppActivity)

    def create_activity(
        self,
        session_id: str,
        app_name: str,
        window_title: str | None,
        duration_seconds: int | None,
        timestamp: datetime,
    ) -> AppActivity:
        activity = AppActivity(
            session_id=session_id,
            app_name=app_name,
            window_title=window_title,
            duration_seconds=duration_seconds,
            timestamp=timestamp,
        )
        return self.add(activity)


class FocusScoreRepository(BaseRepository[FocusScore]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, FocusScore)

    def create_score(self, session_id: str, score: float, level: FocusLevel, timestamp: datetime) -> FocusScore:
        focus_score = FocusScore(session_id=session_id, score=score, level=level, timestamp=timestamp)
        return self.add(focus_score)
