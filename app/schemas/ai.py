from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ChatMessageIn(BaseModel):
    session_id: UUID
    user_id: UUID
    message: str = Field(min_length=1, max_length=4000)


class ChatMessageOut(BaseModel):
    message_id: UUID
    session_id: UUID
    user_id: UUID
    role: str
    content: str
    created_at: datetime


class AIInsightOut(BaseModel):
    insight_id: UUID
    session_id: UUID
    summary: str
    recommendations: list[str]
    created_at: datetime


class ReflectionRequest(BaseModel):
    session_id: UUID


class ReflectionResponse(BaseModel):
    insight: AIInsightOut
