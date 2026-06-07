from cv_service.domain.models import AttentionState, ClassifiedState, DriftThresholds, FrameObservation


class AttentionClassifier:
    def __init__(self, thresholds: DriftThresholds | None = None) -> None:
        self.thresholds = thresholds or DriftThresholds()

    def classify(self, observation: FrameObservation) -> ClassifiedState:
        if not observation.face_detected:
            return ClassifiedState(
                state=AttentionState.away,
                confidence=1.0,
                observation=observation,
                trigger_reason="face_not_detected",
            )

        yaw = abs(observation.yaw)
        pitch = abs(observation.pitch)
        gaze_offset = abs(observation.gaze_offset)

        if yaw <= self.thresholds.yaw_focus and pitch <= self.thresholds.pitch_focus and gaze_offset <= 5 and observation.ear >= self.thresholds.ear_min:
            return ClassifiedState(
                state=AttentionState.focused,
                confidence=0.95,
                observation=observation,
                trigger_reason="aligned_and_alert",
            )

        if yaw > self.thresholds.yaw_disengaged or pitch > self.thresholds.pitch_disengaged or gaze_offset > self.thresholds.gaze_shift:
            return ClassifiedState(
                state=AttentionState.likely_disengaged,
                confidence=0.82,
                observation=observation,
                trigger_reason="large_pose_or_gaze_shift",
            )

        if yaw > self.thresholds.yaw_focus or pitch > self.thresholds.pitch_focus or gaze_offset > 5 or observation.ear < self.thresholds.ear_min:
            return ClassifiedState(
                state=AttentionState.possibly_distracted,
                confidence=0.66,
                observation=observation,
                trigger_reason="moderate_pose_or_ear_change",
            )

        return ClassifiedState(
            state=AttentionState.focused,
            confidence=0.5,
            observation=observation,
            trigger_reason="fallback",
        )
