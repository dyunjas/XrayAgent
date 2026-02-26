import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.logging_config import setup_logging

from app.routers import health, stats, db_health, debug, xray, bearer_api, metrics, web
from app.middleware.prom import PromMiddleware

from app.deps import SessionLocal
from app.services.xray_service import XrayService
from app.services.sync_service import SyncService


setup_logging()
logger = logging.getLogger("xray-agent")

app = FastAPI(
    title=settings.service_name,
    version=settings.version,
    description="Xray agent: sync keys -> xray inbound, plus server stats & metrics.",
)

app.add_middleware(PromMiddleware)
app.mount(
    "/web/static",
    StaticFiles(directory=str(Path(__file__).resolve().parent / "web" / "static")),
    name="web-static",
)

app.include_router(health)
app.include_router(stats)
app.include_router(db_health)
app.include_router(debug)
app.include_router(xray)
app.include_router(bearer_api)
app.include_router(metrics)
app.include_router(web)


@app.on_event("startup")
def startup_sync():
    db = SessionLocal()
    try:
        sync = SyncService(xray=XrayService())
        sync.startup_sync(db)
    finally:
        db.close()
