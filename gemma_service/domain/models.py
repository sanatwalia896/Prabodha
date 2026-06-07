from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True, slots=True)
class SessionSnapshot:
    session_id: str
    user_id: str
    label: str | None
    started_at: datetime
    ended_at: datetime | None
    average_focus: float
    drift_count: int
    top_apps: list[str]
    drift_timeline: list[str]
    journal_entry: str | None = None
    recent_wins: list[str] = field(default_factory=list)
    historical_baseline: str | None = None


@dataclass(frozen=True, slots=True)
class ConversationTurn:
    role: str
    content: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class ReflectionResult:
    summary: str
    recommendations: list[str]
    prompt: str
    model: str
