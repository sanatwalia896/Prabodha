from __future__ import annotations

import argparse
import json
import time

from cv_service.domain.models import FrameObservation
from cv_service.main import analyze_observation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Prabodha CV service.")
    parser.add_argument("--poll-interval", type=float, default=0.5)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    observation = FrameObservation(face_detected=True, yaw=2.0, pitch=1.0, gaze_offset=0.5, ear=0.24)
    while True:
        result = analyze_observation(observation)
        print(json.dumps(result), flush=True)
        time.sleep(args.poll_interval)


if __name__ == "__main__":
    raise SystemExit(main())
