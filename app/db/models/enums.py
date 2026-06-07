from enum import Enum


class AttentionEventType(str, Enum):
    drift = "DRIFT"
    fatigue = "FATIGUE"
    recovery = "RECOVERY"
    focus_gain = "FOCUS_GAIN"
    away = "AWAY"


class FocusLevel(str, Enum):
    deep = "DEEP"
    light = "LIGHT"
    none = "NONE"
