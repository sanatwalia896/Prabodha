from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from uuid import UUID

from app.api.deps import db_session
from app.schemas.ai import AIInsightOut, ChatMessageIn, ChatMessageOut, ReflectionResponse
from app.services.ai_service import AIService

router = APIRouter()


@router.get("/reflect/{session_id}", response_model=AIInsightOut)
def reflect_session(session_id: UUID, db=Depends(db_session)) -> AIInsightOut:
    insight = AIService(db).reflect_session(session_id)
    return AIInsightOut(
        insight_id=insight.insight_id,
        session_id=insight.session_id,
        summary=insight.summary,
        recommendations=insight.recommendations,
        created_at=insight.created_at,
    )


@router.post("/chat", response_model=ChatMessageOut)
def chat_message(payload: ChatMessageIn) -> ChatMessageOut:
    return ChatMessageOut(
        message_id=UUID("00000000-0000-0000-0000-000000000001"),
        session_id=payload.session_id,
        user_id=payload.user_id,
        role="assistant",
        content=f"Not yet wired to live conversation history: {payload.message}",
        created_at=datetime.now(timezone.utc),
    )


@router.get("/chat/history", response_model=list[ChatMessageOut])
def chat_history() -> list[ChatMessageOut]:
    return []
