from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import db_session
from app.schemas.sessions import SessionCreateRequest, SessionDetailResponse, SessionResponse, SessionSummaryResponse
from app.services.session_service import SessionService

router = APIRouter()


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def start_session(payload: SessionCreateRequest, db=Depends(db_session)) -> SessionResponse:
    session_obj = SessionService(db).start_session(payload.user_id, payload.label)
    return SessionResponse(
        session_id=session_obj.session_id,
        user_id=session_obj.user_id,
        label=session_obj.label,
        start_time=session_obj.start_time,
        end_time=session_obj.end_time,
        overall_score=session_obj.overall_score,
    )


@router.post("/{session_id}/stop", response_model=SessionResponse)
def stop_session(session_id: UUID, db=Depends(db_session)) -> SessionResponse:
    session_obj = SessionService(db).stop_session(session_id)
    return SessionResponse(
        session_id=session_obj.session_id,
        user_id=session_obj.user_id,
        label=session_obj.label,
        start_time=session_obj.start_time,
        end_time=session_obj.end_time,
        overall_score=session_obj.overall_score,
    )


@router.get("", response_model=list[SessionResponse])
def list_sessions(user_id: UUID, db=Depends(db_session)) -> list[SessionResponse]:
    sessions = SessionService(db).list_sessions(user_id)
    return [
        SessionResponse(
            session_id=session_obj.session_id,
            user_id=session_obj.user_id,
            label=session_obj.label,
            start_time=session_obj.start_time,
            end_time=session_obj.end_time,
            overall_score=session_obj.overall_score,
        )
        for session_obj in sessions
    ]


@router.get("/{session_id}", response_model=SessionDetailResponse)
def read_session(session_id: UUID, db=Depends(db_session)) -> SessionDetailResponse:
    session_obj = SessionService(db).get_session(session_id)
    summary = SessionService(db).summary(session_id)
    return SessionDetailResponse(
        session_id=session_obj.session_id,
        user_id=session_obj.user_id,
        label=session_obj.label,
        start_time=session_obj.start_time,
        end_time=session_obj.end_time,
        overall_score=session_obj.overall_score,
        drift_count=int(summary["drift_count"]),
        app_count=int(summary["app_count"]),
        focus_samples=int(summary["focus_samples"]),
    )
