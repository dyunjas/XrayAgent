from fastapi import APIRouter
from app.services.stats_service import StatsService
from app.schemas.stats import StatsResponse

router = APIRouter(tags=["stats"])
_stats = StatsService()


@router.get("/stats", response_model=StatsResponse)
def stats():
    return _stats.get_stats().__dict__
