from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path

from app.config import settings


class XrayConfigService:
    def __init__(self, config_path: str | None = None):
        self.config_path = Path(config_path or settings.xray_config_path)

    def read_config(self) -> dict:
        if not self.config_path.exists():
            return {}
        raw = self.config_path.read_text(encoding="utf-8")
        return json.loads(raw) if raw.strip() else {}

    def write_config(self, cfg: dict) -> dict:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"ok": True, "path": str(self.config_path)}

    def summarize(self, cfg: dict) -> dict:
        inbounds = cfg.get("inbounds") if isinstance(cfg, dict) else []
        outbounds = cfg.get("outbounds") if isinstance(cfg, dict) else []
        routing = cfg.get("routing") if isinstance(cfg, dict) else {}
        api = cfg.get("api") if isinstance(cfg, dict) else {}
        return {
            "inbounds_count": len(inbounds) if isinstance(inbounds, list) else 0,
            "outbounds_count": len(outbounds) if isinstance(outbounds, list) else 0,
            "routing_rules_count": len(routing.get("rules", [])) if isinstance(routing, dict) else 0,
            "api_enabled": isinstance(api, dict) and bool(api),
            "loglevel": (cfg.get("log") or {}).get("loglevel") if isinstance(cfg.get("log"), dict) else None,
            "first_inbound_tag": inbounds[0].get("tag") if isinstance(inbounds, list) and inbounds else None,
        }

    def restart_xray(self) -> dict:
        cmd = settings.xray_restart_cmd.strip()
        if not cmd:
            return {"ok": False, "detail": "XRAY_RESTART_CMD is not configured"}
        try:
            parts = shlex.split(cmd)
            p = subprocess.run(parts, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return {"ok": True, "stdout": p.stdout.decode(errors="replace"), "stderr": p.stderr.decode(errors="replace")}
        except subprocess.CalledProcessError as exc:
            return {
                "ok": False,
                "stdout": (exc.stdout or b"").decode(errors="replace"),
                "stderr": (exc.stderr or b"").decode(errors="replace"),
                "detail": str(exc),
            }
