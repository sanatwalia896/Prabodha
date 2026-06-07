from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TrendQuery(BaseModel):
    user_id: UUID


class TrendPoint(BaseModel):
    timestamp: datetime
    focus_score: float


class TrendDataOut(BaseModel):
    points: list[TrendPoint]


class AppUsageOut(BaseModel):
    app_name: str
    total_seconds: int


class PeakHourOut(BaseModel):
    hour: int
    average_focus: float
