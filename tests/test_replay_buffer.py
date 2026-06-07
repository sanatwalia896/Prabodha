from datetime import datetime, timedelta, timezone
from pathlib import Path

from replay_buffer.application.buffer import CircularReplayBuffer
from replay_buffer.application.encoder import ArtifactEncoder
from replay_buffer.application.replay_manager import ReplayBufferManager
from replay_buffer.application.segment_index import SegmentIndex
from replay_buffer.domain.models import ReplayClipRequest, ReplayFrame, SegmentRecord


def make_frame(frame_id: int, minute_offset: int = 0) -> ReplayFrame:
    return ReplayFrame(
        frame_id=frame_id,
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=minute_offset),
        payload=f"frame-{frame_id}".encode("utf-8"),
    )


def test_circular_buffer_keeps_latest_frames() -> None:
    buffer = CircularReplayBuffer(max_frames=3)
    buffer.extend([make_frame(1), make_frame(2), make_frame(3), make_frame(4)])

    snapshot = buffer.snapshot()
    assert [frame.frame_id for frame in snapshot.frames] == [2, 3, 4]


def test_segment_index_evicts_oldest_segment() -> None:
    index = SegmentIndex(max_segments=2)
    index.add(SegmentRecord("seg-1", make_frame(1).timestamp, make_frame(2).timestamp, Path("a.mp4")))
    index.add(SegmentRecord("seg-2", make_frame(2).timestamp, make_frame(3).timestamp, Path("b.mp4")))
    evicted = index.add(SegmentRecord("seg-3", make_frame(3).timestamp, make_frame(4).timestamp, Path("c.mp4")))

    assert [segment.segment_id for segment in evicted] == ["seg-1"]
    assert [path.name for path in index.resolve_paths()] == ["b.mp4", "c.mp4"]


def test_replay_manager_can_write_artifact_clip(tmp_path: Path) -> None:
    manager = ReplayBufferManager(buffer=CircularReplayBuffer(max_frames=5), index=SegmentIndex(), encoder=ArtifactEncoder())
    manager.ingest_frame(make_frame(1))
    manager.ingest_frame(make_frame(2))

    output = tmp_path / "clip.mp4"
    written = manager.save_clip(
        ReplayClipRequest(
            clip_id="clip-1",
            start_time=make_frame(1).timestamp,
            end_time=make_frame(2).timestamp,
            output_path=output,
        )
    )

    assert written == output
    assert output.exists()
    assert "frame-1" in output.read_text(encoding="utf-8")
