from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.db.models import AttentionEventType, FocusLevel, Session as FocusSession, User
from app.repositories.event_repo import AttentionEventRepository, FocusScoreRepository
from app.repositories.session_repo import SessionRepository
from app.repositories.user_repo import UserRepository


def make_session(tmp_path: Path) -> Session:
    engine = create_engine(f"sqlite+pysqlite:///{tmp_path / 'test.db'}", future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)()


def test_database_round_trip(tmp_path: Path) -> None:
    db = make_session(tmp_path)
    try:
        users = UserRepository(db)
        sessions = SessionRepository(db)
        events = AttentionEventRepository(db)
        scores = FocusScoreRepository(db)

        user = users.add(User(username="sam", password_hash="hash"))
        db.commit()

        session_obj = sessions.add(FocusSession(user_id=user.user_id, label="Deep Work"))
        db.commit()

        events.create_attention_event(
            session_id=session_obj.session_id,
            event_type=AttentionEventType.drift,
            confidence=0.92,
            metadata={"gaze_direction": "left"},
            timestamp=datetime.now(timezone.utc),
        )
        scores.create_score(
            session_id=session_obj.session_id,
            score=87.5,
            level=FocusLevel.deep,
            timestamp=datetime.now(timezone.utc),
        )
        db.commit()

        assert users.get_by_username("sam") is not None
        assert sessions.list_for_user(user.user_id)[0].label == "Deep Work"
        assert len(session_obj.attention_events) == 1
        assert len(session_obj.focus_scores) == 1
    finally:
        db.close()
