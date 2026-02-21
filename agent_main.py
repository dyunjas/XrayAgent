import os

import uvicorn

from app.main import app


def main() -> None:
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8020"))
    reload_enabled = os.getenv("RELOAD", "0").lower() in {"1", "true", "yes"}
    uvicorn.run("agent_main:app", host=host, port=port, reload=reload_enabled)


if __name__ == "__main__":
    main()

