from dataclasses import dataclass, field
from enum import Enum


class AttentionState(str, Enum):
    focused = "FOCUSED"
    possibly_distracted = "POSSIBLY_DISTRACTED"
    likely_disengaged = "LIKELY_DISENGAGED"
    away = "AWAY"


@dataclass(frozen=True, slots=True)
class DriftThresholds:
    yaw_focus: float = 15.0
    yaw_disengaged: float = 30.0
    pitch_focus: float = 15.0
    pitch_disengaged: float = 30.0
    gaze_shift: float = 20.0
    ear_min: float = 0.18
    away_window_ratio: float = 0.80
    smoothing_window_size: int = 30


@dataclass(frozen=True, slots=True)
class FrameObservation:
    face_detected: bool
    yaw: float = 0.0
    pitch: float = 0.0
    gaze_offset: float = 0.0
    ear: float = 0.25
    face_center_offset: float = 0.0
    frame_id: int = 0


@dataclass(frozen=True, slots=True)
class ClassifiedState:
    state: AttentionState
    confidence: float
    observation: FrameObservation
    trigger_reason: str = field(default="")
