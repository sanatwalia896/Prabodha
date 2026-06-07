from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.models.replay_clip import ReplayClip
from app.db.models.saved_clip import SavedClip


class MediaService:
    def __init__(self, db: Session, settings: Settings) -> None:
        self.db = db
        self.settings = settings

    def get_clip(self, clip_id: UUID) -> ReplayClip:
        clip = self.db.get(ReplayClip, str(clip_id))
        if clip is None or clip.is_deleted:
            raise ValueError("Clip not found")
        return clip

    def save_clip(self, clip_id: UUID, user_id: UUID, save_note: str | None) -> SavedClip:
        clip = self.get_clip(clip_id)
        saved = SavedClip(clip_id=clip.clip_id, user_id=str(user_id), save_note=save_note)
        self.db.add(saved)
        self.db.commit()
        self.db.refresh(saved)
        return saved

    def delete_clip(self, clip_id: UUID) -> ReplayClip:
        clip = self.get_clip(clip_id)
        clip.is_deleted = True
        file_path = Path(clip.file_path)
        if file_path.exists():
            file_path.unlink()
        self.db.commit()
        self.db.refresh(clip)
        return clip
