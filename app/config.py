import os
from pydantic import BaseModel
from dotenv import load_dotenv


load_dotenv()


class Settings(BaseModel):
    log_level: str = os.getenv("XRAY_LOG_LEVEL", "INFO")

    proto_root: str = os.getenv("XRAY_PROTO_ROOT", "/opt/xray-protos")
    protoc_bin: str = os.getenv("XRAY_PROTOC_BIN", "/usr/bin/protoc")
    grpcurl_bin: str = os.getenv("XRAY_GRPCURL_BIN", "/usr/local/bin/grpcurl")
    protoset: str = os.getenv("XRAY_PROTOSET", f"{os.getenv('XRAY_PROTO_ROOT', '/opt/xray-protos')}/xray.protoset")

    xray_addr: str = os.getenv("XRAY_ADDR", "127.0.0.1:10085")
    inbound_tag: str = os.getenv("XRAY_INBOUND_TAG", "vless-reality-in")
    xray_config_path: str = os.getenv("XRAY_CONFIG_PATH", "/usr/local/etc/xray/config.json")
    xray_restart_cmd: str = os.getenv("XRAY_RESTART_CMD", "")
    xray_bin: str = os.getenv("XRAY_BIN", "/usr/local/bin/xray")

    agent_token: str = os.getenv("XRAY_AGENT_TOKEN", "b54faaef41dfea320e52e25823a8999be3719003a0842910d160a3cd490f6954")

    sync_server_id: int = int(os.getenv("XRAY_SYNC_SERVER_ID", "1"))

    db_dsn: str = (
        os.getenv("XRAY_DB_DSN")
        or os.getenv("PG_DSN")
        or "postgresql+psycopg2://dyunja:Vjq522DkflbCkfd@46.149.71.206:5432/default_db"
    )

    service_name: str = os.getenv("XRAY_AGENT_NAME", "Lunet Panel")
    version: str = os.getenv("XRAY_AGENT_VERSION", "1.0.5")

    xray_public_host: str = os.getenv("XRAY_PUBLIC_HOST", "")
    xray_public_port: int = int(os.getenv("XRAY_PUBLIC_PORT", "443"))
    xray_vless_sni: str = os.getenv("XRAY_VLESS_SNI", "")
    xray_vless_pbk: str = os.getenv("XRAY_VLESS_PBK", "")
    xray_vless_sid: str = os.getenv("XRAY_VLESS_SID", "")
    xray_vless_flow: str = os.getenv("XRAY_VLESS_FLOW", "xtls-rprx-vision")
    xray_vless_security: str = os.getenv("XRAY_VLESS_SECURITY", "reality")
    xray_vless_type: str = os.getenv("XRAY_VLESS_TYPE", "tcp")
    xray_vless_path: str = os.getenv("XRAY_VLESS_PATH", "")

    web_username: str = os.getenv("XRAY_WEB_USERNAME", "admin")
    web_password: str = os.getenv("XRAY_WEB_PASSWORD", "admin")
    web_password_sha256: str = os.getenv("XRAY_WEB_PASSWORD_SHA256", "")
    web_session_secret: str = os.getenv("XRAY_WEB_SESSION_SECRET", os.getenv("XRAY_AGENT_TOKEN", "xray-web-secret"))
    web_session_ttl_sec: int = int(os.getenv("XRAY_WEB_SESSION_TTL_SEC", "86400"))


settings = Settings()
