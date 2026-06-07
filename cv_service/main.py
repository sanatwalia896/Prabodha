from cv_service.domain.models import FrameObservation
from cv_service.application.vision_service import VisionService


def analyze_observation(observation: FrameObservation) -> dict[str, object]:
    decision = VisionService().process(observation)
    return {
        "state": decision.smoothed.state.value,
        "confidence": decision.smoothed.confidence,
        "should_emit_drift_event": decision.smoothed.should_emit_drift_event,
        "reason": decision.classification.trigger_reason,
    }
