from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AttentionEventIn(BaseModel):
    session_id: UUID
    event_type: str = Field(min_length=3, max_length=32)
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: dict[str, object] = Field(default_factory=dict)


class ActivityEventIn(BaseModel):
    session_id: UUID
    app_name: str = Field(min_length=1, max_length=255)
    window_title: str | None = None
    duration_seconds: int | None = Field(default=None, ge=0)


class FocusScoreIn(BaseModel):
    session_id: UUID
    score: float = Field(ge=0.0, le=100.0)
    level: str = Field(min_length=2, max_length=16)


class EventResponse(BaseModel):
    id: str
    session_id: UUID
    created_at: datetime


class RealtimeState(BaseModel):
    session_id: UUID | None = None
    focus_level: float = 0.0
    active_app: str | None = None
    is_user_away: bool = False
    last_event_type: str | None = None
