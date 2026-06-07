from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SessionCreateRequest(BaseModel):
    user_id: UUID
    label: str | None = Field(default=None, max_length=100)


class SessionResponse(BaseModel):
    session_id: UUID
    user_id: UUID
    label: str | None
    start_time: datetime
    end_time: datetime | None
    overall_score: float | None


class SessionSummaryResponse(BaseModel):
    session_id: UUID
    label: str | None
    average_focus: float
    drift_count: int
    app_count: int
    duration_minutes: float


class SessionDetailResponse(SessionResponse):
    drift_count: int = 0
    app_count: int = 0
    focus_samples: int = 0
