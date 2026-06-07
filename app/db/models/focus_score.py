from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.enums import FocusLevel


class FocusScore(Base):
    score_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("session.session_id"), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    score: Mapped[float] = mapped_column(Float, nullable=False)
    level: Mapped[FocusLevel] = mapped_column(String(16), nullable=False)

    session = relationship("Session", back_populates="focus_scores")
