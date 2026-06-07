from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings
from app.db.base import Base
from app.db.models import ReplayClip
from app.repositories.event_repo import AttentionEventRepository
from app.services.ai_service import AIService
from app.services.analytics_service import AnalyticsService
from app.services.auth_service import AuthService
from app.services.event_service import EventService
from app.services.media_service import MediaService
from app.services.session_service import SessionService


def make_session(tmp_path: Path) -> Session:
    engine = create_engine(f"sqlite+pysqlite:///{tmp_path / 'integration.db'}", future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)()


def test_backend_services_work_together(tmp_path: Path) -> None:
    db = make_session(tmp_path)
    settings = Settings(
        database_url=f"sqlite+pysqlite:///{tmp_path / 'integration.db'}",
        media_root=str(tmp_path / "media"),
        jwt_secret="integration-secret",
    )

    try:
        auth = AuthService(db, settings)
        session_service = SessionService(db)
        event_service = EventService(db)
        ai_service = AIService(db)
        analytics = AnalyticsService(db)
        media = MediaService(db, settings)

        user = auth.register("integration-user", "password123")
        token = auth.login("integration-user", "password123")
        assert token

        session_obj = session_service.start_session(user.user_id, "Deep Work")
        event_service.log_score(session_obj.session_id, 86.0, "DEEP")
        event = event_service.log_attention(session_obj.session_id, "DRIFT", 0.94, {"gaze_direction": "left"})
        event_service.log_activity(session_obj.session_id, "VSCode", "main.py", 180)
        session_service.stop_session(session_obj.session_id)

        clip_path = tmp_path / "media" / "clip.mp4"
        clip_path.parent.mkdir(parents=True, exist_ok=True)
        clip_path.write_text("clip data", encoding="utf-8")
        clip = ReplayClip(
            event_id=event.event_id,
            file_path=str(clip_path),
            start_timestamp=datetime.now(timezone.utc),
            end_timestamp=datetime.now(timezone.utc),
        )
        db.add(clip)
        db.commit()

        insight = ai_service.reflect_session(session_obj.session_id)
        trend_points = analytics.trend_points(user.user_id)
        app_usage = analytics.app_usage(user.user_id)
        saved_clip = media.save_clip(clip.clip_id, user.user_id, "Worth reviewing")

        assert insight.recommendations
        assert trend_points
        assert app_usage[0]["app_name"] == "VSCode"
        assert saved_clip.clip_id == clip.clip_id
    finally:
        db.close()
