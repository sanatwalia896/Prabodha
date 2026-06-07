from collections import defaultdict
from datetime import datetime
from uuid import UUID

from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from app.db.models.app_activity import AppActivity
from app.db.models.focus_score import FocusScore
from app.db.models.session import Session as SessionModel


class AnalyticsService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def trend_points(self, user_id: UUID) -> list[dict[str, object]]:
        statement = select(SessionModel).where(SessionModel.user_id == str(user_id)).order_by(SessionModel.start_time.asc())
        sessions = self.db.execute(statement).scalars().all()
        return [
            {"timestamp": session.start_time, "focus_score": float(session.overall_score or 0.0)}
            for session in sessions
        ]

    def app_usage(self, user_id: UUID) -> list[dict[str, object]]:
        statement = (
            select(AppActivity.app_name, func.sum(func.coalesce(AppActivity.duration_seconds, 0)))
            .join(SessionModel, SessionModel.session_id == AppActivity.session_id)
            .where(SessionModel.user_id == str(user_id))
            .group_by(AppActivity.app_name)
            .order_by(func.sum(func.coalesce(AppActivity.duration_seconds, 0)).desc())
        )
        return [{"app_name": row[0], "total_seconds": int(row[1] or 0)} for row in self.db.execute(statement).all()]

    def peak_hours(self, user_id: UUID) -> list[dict[str, object]]:
        statement = (
            select(extract("hour", SessionModel.start_time), func.avg(SessionModel.overall_score))
            .where(SessionModel.user_id == str(user_id))
            .group_by(extract("hour", SessionModel.start_time))
        )
        peaks = []
        for hour_text, average_score in self.db.execute(statement).all():
            peaks.append({"hour": int(hour_text or 0), "average_focus": float(average_score or 0.0)})
        return peaks
