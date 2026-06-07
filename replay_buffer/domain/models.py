from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ReplayFrame:
    frame_id: int
    timestamp: datetime
    payload: bytes


@dataclass(frozen=True, slots=True)
class SegmentRecord:
    segment_id: str
    start_time: datetime
    end_time: datetime
    file_path: Path


@dataclass(frozen=True, slots=True)
class ReplayClipRequest:
    clip_id: str
    start_time: datetime
    end_time: datetime
    output_path: Path
