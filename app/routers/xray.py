import uuid
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_db, auth_dep
from app.services.xray_service import XrayService
from app.services.sync_service import SyncService
from app.schemas.xray import (
    AddUserReq, AddUserOK,
    RemoveUserReq, RemoveUserOK,
    ResyncOK,
)
from app.utils.email import email_for_user_id
from app.utils.http_errors import http_unprocessable

logger = logging.getLogger("xray-agent")
router = APIRouter(tags=["xray"])

xray = XrayService()
sync = SyncService(xray=xray)


@router.post(
    "/resync",
    response_model=ResyncOK,
    dependencies=[Depends(auth_dep)],
    responses={
        401: {"description": "Unauthorized"},
        500: {"description": "Xray grpc/proto error"},
    },
)
def resync(db: Session = Depends(get_db)):
    return sync.resync(db)


@router.post(
    "/add_user",
    response_model=AddUserOK,
    dependencies=[Depends(auth_dep)],
    responses={
        401: {"description": "Unauthorized"},
        422: {"description": "Validation error"},
        500: {"description": "Xray grpc/proto error"},
    },
)
def add_user(req: AddUserReq):
    email = req.email
    if not email:
        if req.db_user_id is None:
            raise http_unprocessable("email or db_user_id is required")
        email = email_for_user_id(req.db_user_id)

    uid = req.user_id or str(uuid.uuid4())

    try:
        out = xray.add_user(email=email, level=req.level, uid=uid)
        logger.info("[add_user] OK uuid=%s email=%s", uid, email)
        return {"ok": True, "uuid": uid, "email": email, "grpc": out}
    except HTTPException as e:
        if xray.is_already_exists_error(str(e.detail)):
            logger.info("[add_user] ALREADY uuid=%s email=%s", uid, email)
            return {"ok": True, "uuid": uid, "email": email, "note": "already exists"}
        raise


@router.post(
    "/remove_user",
    response_model=RemoveUserOK,
    dependencies=[Depends(auth_dep)],
    responses={
        401: {"description": "Unauthorized"},
        500: {"description": "Xray grpc/proto error"},
    },
)
def remove_user(req: RemoveUserReq):
    out = xray.remove_user(email=req.email)
    logger.info("[remove_user] OK email=%s", req.email)
    return {"ok": True, "grpc": out}
