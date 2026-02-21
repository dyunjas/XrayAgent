import base64
from app.config import settings
from app.utils.subprocess_run import run_cmd


def encode_proto(type_name: str, textproto: str, proto_rel_path: str) -> bytes:
    cmd = [
        settings.protoc_bin,
        f"--encode={type_name}",
        "-I", settings.proto_root,
        "-I", f"{settings.proto_root}/common",
        "-I", f"{settings.proto_root}/app",
        "-I", f"{settings.proto_root}/proxy",
        "-I", f"{settings.proto_root}/infra",
        "-I", f"{settings.proto_root}/transport",
        "-I", f"{settings.proto_root}/core",
        f"{settings.proto_root}/{proto_rel_path}",
    ]
    return run_cmd(cmd, stdin=textproto.encode())


def bytes_to_hex_escape(data: bytes) -> str:
    return "".join(f"\\x{b:02x}" for b in data)


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode()
