import json
import time
from fastapi import HTTPException

from app.config import settings
from app.utils.subprocess_run import run_cmd


class TrafficService:
    def __init__(self):
        self._online_cache: dict[str, dict[str, int | float]] = {}

    @staticmethod
    def _is_stat_missing_error(exc: Exception) -> bool:
        detail = ""
        if isinstance(exc, HTTPException):
            detail = str(exc.detail or "")
        else:
            detail = str(exc or "")
        low = detail.lower()
        return "not found" in low or "notfound" in low or "unknown stat" in low

    @staticmethod
    def _is_service_unavailable_error(exc: Exception) -> bool:
        detail = str(getattr(exc, "detail", exc)).lower()
        return "does not expose service" in detail or "unimplemented" in detail

    def _get_stat_via_xray_cli(self, name: str, *, reset: bool = False) -> dict:
        cmd = [
            settings.xray_bin,
            "api",
            "stats",
            f"--server={settings.xray_addr}",
            "-name",
            name,
        ]
        if reset:
            cmd.append("-reset")
        raw = run_cmd(cmd).decode(errors="replace").strip()
        data = json.loads(raw) if raw else {}
        value = int((data or {}).get("value", 0))
        return {"ok": True, "name": name, "value": value, "missing": False}

    def _get_stat(self, name: str, *, reset: bool = False) -> dict:
        payload = json.dumps({"name": name, "reset": reset}, separators=(",", ":"))
        last_exc: Exception | None = None
        for method in (
            "xray.app.stats.command.StatsService/GetStats",
            "v2ray.core.app.stats.command.StatsService/GetStats",
        ):
            try:
                raw = run_cmd([
                    settings.grpcurl_bin,
                    "-plaintext",
                    "-protoset",
                    settings.protoset,
                    "-d",
                    payload,
                    settings.xray_addr,
                    method,
                ]).decode()
                break
            except Exception as exc:
                last_exc = exc
                # Xray may return "not found" for counters that were not created yet.
                # This still means StatsService is reachable, so expose zero value.
                if self._is_stat_missing_error(exc):
                    return {"ok": True, "name": name, "value": 0, "missing": True}
                if self._is_service_unavailable_error(exc):
                    try:
                        return self._get_stat_via_xray_cli(name, reset=reset)
                    except Exception:
                        continue
                raise
        else:
            if last_exc is not None:
                raise last_exc
            raise RuntimeError("StatsService call failed without explicit exception")
        data = json.loads(raw) if raw else {}

        stat = data.get("stat") or {}
        value = int(stat.get("value", 0))
        return {"ok": True, "name": name, "value": value, "missing": False}

    def get_inbound_traffic(self) -> dict:
        try:
            up = self._get_stat(f"inbound>>>{settings.inbound_tag}>>>traffic>>>uplink")
            down = self._get_stat(f"inbound>>>{settings.inbound_tag}>>>traffic>>>downlink")
            return {
                "available": True,
                "uplink": up["value"],
                "downlink": down["value"],
                "total": up["value"] + down["value"],
            }
        except Exception:
            return {
                "available": False,
                "uplink": 0,
                "downlink": 0,
                "total": 0,
            }

    def get_users_traffic(self, emails: list[str]) -> dict[str, dict]:
        out: dict[str, dict] = {}
        for email in emails:
            try:
                up = self._get_stat(f"user>>>{email}>>>traffic>>>uplink")
                down = self._get_stat(f"user>>>{email}>>>traffic>>>downlink")
                out[email] = {
                    "available": True,
                    "uplink": up["value"],
                    "downlink": down["value"],
                    "total": up["value"] + down["value"],
                }
            except Exception:
                out[email] = {
                    "available": False,
                    "uplink": 0,
                    "downlink": 0,
                    "total": 0,
                }
        return out

    def get_users_online(self, emails: list[str], traffic_map: dict[str, dict] | None = None) -> dict[str, dict]:
        out: dict[str, dict] = {}
        now = time.time()
        activity_window = max(15, int(settings.xray_online_activity_window_sec))
        for email in emails:
            # Newer Xray builds may expose per-user online counters when enabled in policy stats.
            # If not available, we return supported=False and online=False.
            supported = False
            value = 0
            for stat_name in (
                f"user>>>{email}>>>online",
                f"user>>>{email}>>>online>>>count",
            ):
                try:
                    stat = self._get_stat(stat_name)
                    value = int(stat["value"])
                    supported = True
                    break
                except Exception:
                    continue

            inferred = False
            if not supported:
                traffic = (traffic_map or {}).get(email)
                if traffic is None:
                    traffic = self.get_users_traffic([email]).get(email, {"total": 0})
                total = int((traffic or {}).get("total", 0))
                state = self._online_cache.get(email, {"last_total": total, "last_seen": now, "last_active": 0.0})
                last_total = int(state.get("last_total", total))
                last_active = float(state.get("last_active", 0.0))
                if total > last_total:
                    last_active = now
                is_online = (now - last_active) <= activity_window if last_active > 0 else False
                self._online_cache[email] = {
                    "last_total": total,
                    "last_seen": now,
                    "last_active": last_active,
                }
                inferred = True

            out[email] = {
                "supported": supported or inferred,
                "online": bool(value > 0) if supported else bool(is_online if inferred else False),
                "value": int(value),
                "inferred": inferred,
            }
        return out

    def reset_inbound_traffic(self) -> dict:
        try:
            up = self._get_stat(f"inbound>>>{settings.inbound_tag}>>>traffic>>>uplink", reset=True)
            down = self._get_stat(f"inbound>>>{settings.inbound_tag}>>>traffic>>>downlink", reset=True)
            return {
                "ok": True,
                "available": True,
                "reset_uplink": up["value"],
                "reset_downlink": down["value"],
                "reset_total": up["value"] + down["value"],
            }
        except Exception:
            return {
                "ok": False,
                "available": False,
                "reset_uplink": 0,
                "reset_downlink": 0,
                "reset_total": 0,
            }

    def reset_users_traffic(self, emails: list[str]) -> dict:
        total_up = 0
        total_down = 0
        available = False

        for email in emails:
            try:
                up = self._get_stat(f"user>>>{email}>>>traffic>>>uplink", reset=True)
                down = self._get_stat(f"user>>>{email}>>>traffic>>>downlink", reset=True)
                total_up += up["value"]
                total_down += down["value"]
                available = True
            except Exception:
                continue

        return {
            "ok": available,
            "available": available,
            "reset_uplink": total_up,
            "reset_downlink": total_down,
            "reset_total": total_up + total_down,
        }
