from typing import Optional
from fastapi import HTTPException

from app.config import settings



def require_bearer(authorization: Optional[str]) -> None:
    token = settings.agent_token
    if not token:
        return

    if not authorization or authorization != f"Bearer {token}":
        raise HTTPException(status_code=401, detail="Unauthorized")