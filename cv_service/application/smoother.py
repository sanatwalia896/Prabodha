from collections import Counter, deque
from dataclasses import dataclass

from cv_service.domain.models import AttentionState, ClassifiedState, DriftThresholds, FrameObservation


@dataclass(frozen=True, slots=True)
class SmoothedState:
    state: AttentionState
    confidence: float
    window_size: int
    raw_states: tuple[AttentionState, ...]
    should_emit_drift_event: bool


class TemporalSmoother:
    def __init__(self, thresholds: DriftThresholds | None = None) -> None:
        self.thresholds = thresholds or DriftThresholds()
        self._window: deque[ClassifiedState] = deque(maxlen=self.thresholds.smoothing_window_size)

    def add(self, classification: ClassifiedState) -> SmoothedState:
        self._window.append(classification)
        raw_states = tuple(item.state for item in self._window)
        state, count = Counter(raw_states).most_common(1)[0]
        confidence = count / len(raw_states)
        should_emit_drift_event = (
            len(raw_states) == self.thresholds.smoothing_window_size
            and confidence >= self.thresholds.away_window_ratio
            and state in {AttentionState.possibly_distracted, AttentionState.likely_disengaged, AttentionState.away}
        )
        return SmoothedState(
            state=state,
            confidence=confidence,
            window_size=len(raw_states),
            raw_states=raw_states,
            should_emit_drift_event=should_emit_drift_event,
        )
