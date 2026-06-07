from dataclasses import dataclass

from cv_service.application.classifier import AttentionClassifier
from cv_service.application.smoother import SmoothedState, TemporalSmoother
from cv_service.domain.models import ClassifiedState, DriftThresholds, FrameObservation


@dataclass(frozen=True, slots=True)
class VisionDecision:
    classification: ClassifiedState
    smoothed: SmoothedState


class VisionService:
    def __init__(self, thresholds: DriftThresholds | None = None) -> None:
        self.classifier = AttentionClassifier(thresholds)
        self.smoother = TemporalSmoother(thresholds)

    def process(self, observation: FrameObservation) -> VisionDecision:
        classification = self.classifier.classify(observation)
        smoothed = self.smoother.add(classification)
        return VisionDecision(classification=classification, smoothed=smoothed)
