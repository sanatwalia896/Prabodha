from fastapi import APIRouter, Depends

from app.api.deps import db_session
from app.schemas.events import ActivityEventIn, AttentionEventIn, EventResponse, FocusScoreIn
from app.services.event_service import EventService

router = APIRouter()


@router.post("/attention", response_model=EventResponse)
def log_attention_event(payload: AttentionEventIn, db=Depends(db_session)) -> EventResponse:
    service = EventService(db)
    event = service.log_attention(payload.session_id, payload.event_type, payload.confidence, payload.metadata)
    return EventResponse(id=event.event_id, session_id=event.session_id, created_at=event.timestamp)


@router.post("/activity", response_model=EventResponse)
def log_activity_event(payload: ActivityEventIn, db=Depends(db_session)) -> EventResponse:
    service = EventService(db)
    activity = service.log_activity(payload.session_id, payload.app_name, payload.window_title, payload.duration_seconds)
    return EventResponse(id=str(activity.activity_id), session_id=activity.session_id, created_at=activity.timestamp)


@router.post("/score", response_model=EventResponse)
def log_focus_score(payload: FocusScoreIn, db=Depends(db_session)) -> EventResponse:
    service = EventService(db)
    score = service.log_score(payload.session_id, payload.score, payload.level)
    return EventResponse(id=str(score.score_id), session_id=score.session_id, created_at=score.timestamp)
