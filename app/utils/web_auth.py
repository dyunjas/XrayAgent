import base64
import hashlib
import hmac
import json
import time

from app.config import settings


def _b64_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _b64_decode(raw: str) -> bytes:
    pad = "=" * ((4 - len(raw) % 4) % 4)
    return base64.urlsafe_b64decode(raw + pad)


def verify_credentials(nick: str, password: str) -> bool:
    if not hmac.compare_digest(nick, settings.web_username):
        return False

    if settings.web_password_sha256:
        hashed = hashlib.sha256(password.encode()).hexdigest()
        return hmac.compare_digest(hashed, settings.web_password_sha256.lower())

    return hmac.compare_digest(password, settings.web_password)


def create_session_token(nick: str) -> str:
    payload = {
        "nick": nick,
        "exp": int(time.time()) + settings.web_session_ttl_sec,
    }
    payload_b64 = _b64_encode(json.dumps(payload, separators=(",", ":")).encode())
    sig = hmac.new(settings.web_session_secret.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
    return f"{payload_b64}.{sig}"


def get_nick_from_session(token: str | None) -> str | None:
    if not token:
        return None
    try:
        payload_b64, sig = token.split(".", 1)
    except ValueError:
        return None

    expected = hmac.new(settings.web_session_secret.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig):
        return None

    try:
        payload = json.loads(_b64_decode(payload_b64))
    except Exception:
        return None

    if int(payload.get("exp", 0)) < int(time.time()):
        return None

    nick = payload.get("nick")
    if not isinstance(nick, str):
        return None
    return nick
