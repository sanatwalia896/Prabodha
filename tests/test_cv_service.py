from cv_service.application.classifier import AttentionClassifier
from cv_service.application.smoother import TemporalSmoother
from cv_service.domain.models import AttentionState, FrameObservation


def test_classifier_marks_face_missing_as_away() -> None:
    classifier = AttentionClassifier()
    result = classifier.classify(FrameObservation(face_detected=False))

    assert result.state == AttentionState.away
    assert result.confidence == 1.0


def test_classifier_marks_strong_focus_as_focused() -> None:
    classifier = AttentionClassifier()
    result = classifier.classify(
        FrameObservation(face_detected=True, yaw=2.0, pitch=3.0, gaze_offset=1.0, ear=0.24)
    )

    assert result.state == AttentionState.focused
    assert result.trigger_reason == "aligned_and_alert"


def test_smoother_triggers_drift_after_consistent_non_focus() -> None:
    smoother = TemporalSmoother()

    last = None
    for frame_id in range(30):
        last = smoother.add(
            AttentionClassifier().classify(
                FrameObservation(face_detected=True, yaw=35.0, pitch=5.0, gaze_offset=1.0, frame_id=frame_id)
            )
        )

    assert last is not None
    assert last.state == AttentionState.likely_disengaged
    assert last.should_emit_drift_event is True
