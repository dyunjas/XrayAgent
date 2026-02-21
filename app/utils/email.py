from app.models import Key


def email_for_key(k: Key) -> str:
    return f"user-{k.user_id}@lunet"


def email_for_user_id(uid: int) -> str:
    return f"user-{uid}@lunet"
