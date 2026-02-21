import time
import logging
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.config import settings
from app.models import Key, KeyStatus
from app.services.xray_service import XrayService
from app.utils.email import email_for_key


logger = logging.getLogger("xray-agent")


class SyncService:
    def __init__(self, xray: XrayService):
        self.xray = xray

    def get_active_keys(self, db: Session) -> list[Key]:
        return db.execute(
            select(Key).where(
                Key.status == KeyStatus.active,
                Key.server_id == settings.sync_server_id,
            )
        ).scalars().all()

    def resync(self, db: Session) -> dict[str, Any]:
        active = self.get_active_keys(db)
        details: list[dict[str, Any]] = []

        logger.info("[resync] server_id=%s active=%s", settings.sync_server_id, len(active))

        for k in active:
            email = email_for_key(k)
            logger.info("[resync] CANDIDATE uuid=%s email=%s", k.uuid, email)
            try:
                self.xray.add_user(email=email, level=0, uid=k.uuid)
                details.append({"uuid": k.uuid, "email": email, "result": "ok"})
            except HTTPException as e:
                if self.xray.is_already_exists_error(str(e.detail)):
                    details.append({"uuid": k.uuid, "email": email, "result": "already"})
                else:
                    details.append({"uuid": k.uuid, "email": email, "result": "error", "error": str(e.detail)})

        return {
            "ok": True,
            "synced": sum(1 for d in details if d["result"] in ("ok", "already")),
            "failed": [d for d in details if d["result"] == "error"],
            "details": details,
        }

    def startup_sync(self, db: Session, attempts: int = 3) -> None:
        active = self.get_active_keys(db)
        total = len(active)
        logger.info("[startup-sync] begin server_id=%s active=%s", settings.sync_server_id, total)

        for attempt in range(1, attempts + 1):
            try:
                synced = 0
                for k in active:
                    email = email_for_key(k)
                    logger.info("[startup-sync] CANDIDATE uuid=%s email=%s", k.uuid, email)
                    try:
                        self.xray.add_user(email=email, level=0, uid=k.uuid)
                        logger.info("[startup-sync] OK uuid=%s", k.uuid)
                        synced += 1
                    except HTTPException as e:
                        if self.xray.is_already_exists_error(str(e.detail)):
                            logger.info("[startup-sync] ALREADY uuid=%s", k.uuid)
                            synced += 1
                        else:
                            logger.error("[startup-sync] ERR uuid=%s err=%s", k.uuid, e.detail)
                logger.info("[startup-sync] finished attempt %s/%s synced=%s/%s", attempt, attempts, synced, total)
                return
            except Exception as e:
                logger.error("[startup-sync] attempt %s failed: %s", attempt, e)
                if attempt < attempts:
                    time.sleep(2)
                else:
                    logger.error("[startup-sync] giving up after retries")
