from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.deps import get_db
from app.services.db_service import DBService
from app.schemas.debug import ActiveKeysCountOK, ActiveKeysCountFail

router = APIRouter(tags=["debug"])
svc = DBService()


@router.get("/debug/active_keys_count", response_model=ActiveKeysCountOK | ActiveKeysCountFail)
def active_keys_count(db: Session = Depends(get_db)):
    return svc.active_keys_count(db, server_id=settings.sync_server_id)
