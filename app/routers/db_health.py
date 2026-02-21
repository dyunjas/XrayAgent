from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_db
from app.services.db_service import DBService
from app.schemas.db import DBHealthOK, DBHealthFail

router = APIRouter(tags=["db"])
svc = DBService()


@router.get("/db_health", response_model=DBHealthOK | DBHealthFail)
def db_health(db: Session = Depends(get_db)):
    return svc.db_health(db)
