from abc import ABC, abstractmethod
from pathlib import Path

from replay_buffer.domain.models import ReplayFrame


class VideoEncoder(ABC):
    @abstractmethod
    def encode(self, frames: tuple[ReplayFrame, ...], output_path: Path) -> Path:
        raise NotImplementedError


class OpenCVVideoEncoder(VideoEncoder):  # pragma: no cover - optional dependency
    def __init__(self) -> None:
        try:
            import cv2  # type: ignore
        except ImportError as exc:
            raise RuntimeError("OpenCV is required for video encoding") from exc
        self._cv2 = cv2

    def encode(self, frames: tuple[ReplayFrame, ...], output_path: Path) -> Path:
        raise RuntimeError("OpenCV encoding is not wired in this environment")


class ArtifactEncoder(VideoEncoder):
    def encode(self, frames: tuple[ReplayFrame, ...], output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        summary = "\n".join(
            f"{frame.frame_id},{frame.timestamp.isoformat()},{len(frame.payload)},{frame.payload.decode('utf-8', errors='replace')}"
            for frame in frames
        )
        output_path.write_text(summary, encoding="utf-8")
        return output_path
