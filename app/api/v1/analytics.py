from fastapi import APIRouter, Depends
from uuid import UUID

from app.api.deps import db_session
from app.schemas.analytics import AppUsageOut, PeakHourOut, TrendDataOut, TrendPoint
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/trends", response_model=TrendDataOut)
def trend_data(user_id: UUID, db=Depends(db_session)) -> TrendDataOut:
    points = AnalyticsService(db).trend_points(user_id)
    return TrendDataOut(points=[TrendPoint(**point) for point in points])


@router.get("/apps", response_model=list[AppUsageOut])
def app_usage(user_id: UUID, db=Depends(db_session)) -> list[AppUsageOut]:
    return [AppUsageOut(**row) for row in AnalyticsService(db).app_usage(user_id)]


@router.get("/peak", response_model=list[PeakHourOut])
def peak_hours(user_id: UUID, db=Depends(db_session)) -> list[PeakHourOut]:
    return [PeakHourOut(**row) for row in AnalyticsService(db).peak_hours(user_id)]
