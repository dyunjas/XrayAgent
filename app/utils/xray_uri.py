from urllib.parse import urlencode

from app.config import settings


def build_vless_uri(*, uid: str, email: str) -> str | None:
    if not settings.xray_public_host:
        return None

    query = {
        "type": settings.xray_vless_type,
        "security": settings.xray_vless_security,
        "sni": settings.xray_vless_sni,
        "pbk": settings.xray_vless_pbk,
        "sid": settings.xray_vless_sid,
        "flow": settings.xray_vless_flow,
        "path": settings.xray_vless_path,
    }
    filtered = {k: v for k, v in query.items() if str(v or "").strip()}
    encoded = urlencode(filtered, safe="/")
    suffix = f"?{encoded}" if encoded else ""
    return f"vless://{uid}@{settings.xray_public_host}:{settings.xray_public_port}{suffix}#{email}"
