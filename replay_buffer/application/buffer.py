from collections import deque
from dataclasses import dataclass
from datetime import datetime

from replay_buffer.domain.models import ReplayFrame


@dataclass(frozen=True, slots=True)
class BufferSnapshot:
    frames: tuple[ReplayFrame, ...]
    start_time: datetime | None
    end_time: datetime | None


class CircularReplayBuffer:
    def __init__(self, max_frames: int = 900) -> None:
        if max_frames <= 0:
            raise ValueError("max_frames must be positive")
        self.max_frames = max_frames
        self._frames: deque[ReplayFrame] = deque(maxlen=max_frames)

    def append(self, frame: ReplayFrame) -> None:
        self._frames.append(frame)

    def extend(self, frames: list[ReplayFrame]) -> None:
        for frame in frames:
            self.append(frame)

    def snapshot(self) -> BufferSnapshot:
        frames = tuple(self._frames)
        if not frames:
            return BufferSnapshot(frames=(), start_time=None, end_time=None)
        return BufferSnapshot(frames=frames, start_time=frames[0].timestamp, end_time=frames[-1].timestamp)

    def window_since(self, cutoff: datetime) -> tuple[ReplayFrame, ...]:
        return tuple(frame for frame in self._frames if frame.timestamp >= cutoff)
