def mask_dsn(dsn: str) -> str:
    try:
        prefix, rest = dsn.split("://", 1)
        creds, host = rest.split("@", 1)
        if ":" in creds:
            user, _ = creds.split(":", 1)
            creds = f"{user}:***"
        return f"{prefix}://{creds}@{host}"
    except Exception:
        return dsn
