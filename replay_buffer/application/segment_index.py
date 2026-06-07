from collections import OrderedDict
from datetime import datetime
from pathlib import Path

from replay_buffer.domain.models import SegmentRecord


class SegmentIndex:
    def __init__(self, max_segments: int = 10) -> None:
        if max_segments <= 0:
            raise ValueError("max_segments must be positive")
        self.max_segments = max_segments
        self._segments: OrderedDict[str, SegmentRecord] = OrderedDict()

    def add(self, record: SegmentRecord) -> list[SegmentRecord]:
        self._segments[record.segment_id] = record
        evicted: list[SegmentRecord] = []
        while len(self._segments) > self.max_segments:
            _, removed = self._segments.popitem(last=False)
            evicted.append(removed)
        return evicted

    def latest(self, count: int) -> list[SegmentRecord]:
        if count <= 0:
            return []
        return list(self._segments.values())[-count:]

    def resolve_paths(self) -> list[Path]:
        return [segment.file_path for segment in self._segments.values()]
