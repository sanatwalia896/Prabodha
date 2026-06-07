from datetime import datetime
from pathlib import Path

from replay_buffer.application.buffer import CircularReplayBuffer, BufferSnapshot
from replay_buffer.application.encoder import VideoEncoder
from replay_buffer.application.segment_index import SegmentIndex
from replay_buffer.domain.models import ReplayClipRequest, ReplayFrame, SegmentRecord


class ReplayBufferManager:
    def __init__(
        self,
        buffer: CircularReplayBuffer | None = None,
        index: SegmentIndex | None = None,
        encoder: VideoEncoder | None = None,
    ) -> None:
        self.buffer = buffer or CircularReplayBuffer()
        self.index = index or SegmentIndex()
        self.encoder = encoder

    def ingest_frame(self, frame: ReplayFrame) -> None:
        self.buffer.append(frame)

    def rotate_segment(self, segment_id: str, file_path: Path, start_time: datetime, end_time: datetime) -> list[SegmentRecord]:
        record = SegmentRecord(segment_id=segment_id, start_time=start_time, end_time=end_time, file_path=file_path)
        return self.index.add(record)

    def save_clip(self, request: ReplayClipRequest, include_latest_segments: int = 1) -> Path:
        if self.encoder is None:
            raise RuntimeError("No video encoder configured")
        frames = self.buffer.snapshot().frames
        if include_latest_segments > 0:
            for segment in self.index.latest(include_latest_segments):
                if segment.file_path.exists():
                    pass
        return self.encoder.encode(frames, request.output_path)

    def snapshot(self) -> BufferSnapshot:
        return self.buffer.snapshot()
