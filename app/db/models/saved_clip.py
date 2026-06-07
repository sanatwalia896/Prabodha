from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SavedClip(Base):
    save_id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
    clip_id: Mapped[str] = mapped_column(ForeignKey("replayclip.clip_id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.user_id"), nullable=False, index=True)
    save_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    clip = relationship("ReplayClip", back_populates="saved_clips")
    user = relationship("User", back_populates="saved_clips")
