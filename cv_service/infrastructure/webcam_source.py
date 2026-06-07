from collections.abc import Iterator

from cv_service.domain.models import FrameObservation


class WebcamNotAvailableError(RuntimeError):
    pass


class WebcamFrameSource:
    def __init__(self, device_index: int = 0) -> None:
        self.device_index = device_index
        try:
            import cv2  # type: ignore
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise WebcamNotAvailableError("OpenCV is not installed") from exc
        self._cv2 = cv2

    def stream(self) -> Iterator[FrameObservation]:  # pragma: no cover - hardware dependent
        camera = self._cv2.VideoCapture(self.device_index)
        if not camera.isOpened():
            raise WebcamNotAvailableError(f"Cannot open webcam device {self.device_index}")
        frame_id = 0
        try:
            while True:
                ok, _frame = camera.read()
                if not ok:
                    break
                frame_id += 1
                yield FrameObservation(face_detected=True, frame_id=frame_id)
        finally:
            camera.release()
