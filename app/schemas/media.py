from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SaveClipIn(BaseModel):
    user_id: UUID
    save_note: str | None = Field(default=None, max_length=2000)


class SavedClipOut(BaseModel):
    save_id: UUID
    clip_id: UUID
    user_id: UUID
    save_note: str | None
    created_at: datetime


class ClipOut(BaseModel):
    clip_id: UUID
    file_path: str
    start_timestamp: datetime
    end_timestamp: datetime
    is_deleted: bool
