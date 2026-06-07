from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from uuid import UUID

from app.api.deps import db_session
from app.schemas.media import ClipOut, SaveClipIn, SavedClipOut
from app.services.media_service import MediaService
from app.core.config import get_settings

router = APIRouter()


@router.get("/replays/{clip_id}", response_class=FileResponse)
def stream_clip(clip_id: UUID, db=Depends(db_session)):
    clip = MediaService(db, get_settings()).get_clip(clip_id)
    return FileResponse(clip.file_path, media_type="video/mp4", filename=f"{clip.clip_id}.mp4")


@router.post("/save/{clip_id}", response_model=SavedClipOut)
def save_clip(clip_id: UUID, payload: SaveClipIn, db=Depends(db_session)) -> SavedClipOut:
    saved = MediaService(db, get_settings()).save_clip(clip_id, payload.user_id, payload.save_note)
    return SavedClipOut(
        save_id=saved.save_id,
        clip_id=saved.clip_id,
        user_id=saved.user_id,
        save_note=saved.save_note,
        created_at=saved.created_at,
    )


@router.delete("/clips/{clip_id}")
def delete_clip(clip_id: UUID, db=Depends(db_session)) -> dict[str, str]:
    MediaService(db, get_settings()).delete_clip(clip_id)
    return {"status": "deleted"}
