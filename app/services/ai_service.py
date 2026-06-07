from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.ai_insight import AIInsight
from app.db.models.app_activity import AppActivity
from app.db.models.focus_score import FocusScore
from app.db.models.journal import Journal
from app.db.models.session import Session as SessionModel
from gemma_service.application.client import DummyLLMClient
from gemma_service.application.gemma_service import GemmaReflectionService
from gemma_service.domain.models import SessionSnapshot


class AIService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.gemma = GemmaReflectionService(client=DummyLLMClient())

    def reflect_session(self, session_id: UUID) -> AIInsight:
        snapshot = self._build_snapshot(str(session_id))
        history = self._build_history(str(session_id))
        result = self.gemma.reflect(snapshot, history)
        insight = AIInsight(
            session_id=str(session_id),
            summary=result.summary,
            recommendations=result.recommendations,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(insight)
        self.db.commit()
        self.db.refresh(insight)
        return insight

    def get_latest_insight(self, session_id: UUID) -> AIInsight | None:
        statement = select(AIInsight).where(AIInsight.session_id == str(session_id)).order_by(AIInsight.created_at.desc())
        return self.db.execute(statement).scalar_one_or_none()

    def _build_snapshot(self, session_id: str) -> SessionSnapshot:
        session_obj = self.db.get(SessionModel, session_id)
        if session_obj is None:
            raise ValueError("Session not found")
        scores = self.db.execute(select(FocusScore).where(FocusScore.session_id == session_id)).scalars().all()
        activities = self.db.execute(select(AppActivity).where(AppActivity.session_id == session_id)).scalars().all()
        journal = self.db.execute(select(Journal).where(Journal.session_id == session_id).order_by(Journal.created_at.desc())).scalars().first()
        average_focus = float(sum(score.score for score in scores) / len(scores)) if scores else float(session_obj.overall_score or 0.0)
        drift_count = len([score for score in scores if score.score < 70]) or len(activities)
        top_apps = self._top_apps(activities)
        timeline = [f"T+{index * 5}m: activity change around {activity.app_name}" for index, activity in enumerate(activities[:5])]
        return SessionSnapshot(
            session_id=session_obj.session_id,
            user_id=session_obj.user_id,
            label=session_obj.label,
            started_at=session_obj.start_time,
            ended_at=session_obj.end_time,
            average_focus=average_focus,
            drift_count=drift_count,
            top_apps=top_apps,
            drift_timeline=timeline,
            journal_entry=journal.content if journal else None,
            recent_wins=[],
            historical_baseline="Based on the last 14 days of sessions.",
        )

    def _build_history(self, session_id: str) -> list[str]:
        activities = self.db.execute(select(AppActivity).where(AppActivity.session_id == session_id)).scalars().all()
        if not activities:
            return []
        return [f"{activity.app_name}: {activity.window_title or 'No title'}" for activity in activities[:10]]

    @staticmethod
    def _top_apps(activities: list[AppActivity]) -> list[str]:
        counts: dict[str, int] = {}
        for activity in activities:
            counts[activity.app_name] = counts.get(activity.app_name, 0) + 1
        return [name for name, _count in sorted(counts.items(), key=lambda item: item[1], reverse=True)[:3]]
