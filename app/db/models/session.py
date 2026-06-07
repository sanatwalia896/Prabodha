from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Session(Base):
    session_id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("user.user_id"), nullable=False, index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    label: Mapped[str | None] = mapped_column(String(100), nullable=True)
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="sessions")
    attention_events = relationship("AttentionEvent", back_populates="session", cascade="all, delete-orphan")
    app_activity = relationship("AppActivity", back_populates="session", cascade="all, delete-orphan")
    focus_scores = relationship("FocusScore", back_populates="session", cascade="all, delete-orphan")
    ai_insights = relationship("AIInsight", back_populates="session", cascade="all, delete-orphan")
    journals = relationship("Journal", back_populates="session", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    system_metrics = relationship("SystemMetric", back_populates="session", cascade="all, delete-orphan")
