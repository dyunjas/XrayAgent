from fastapi import HTTPException
from app.config import settings
from app.utils.grpc_codec import encode_proto, bytes_to_hex_escape, b64
from app.utils.subprocess_run import run_cmd


class XrayService:
    def add_user(self, *, email: str, level: int, uid: str) -> str:
        account_text = f'id: "{uid}"\n'
        account_bin = encode_proto("xray.proxy.vless.Account", account_text, "proxy/vless/account.proto")
        account_hex = bytes_to_hex_escape(account_bin)

        add_user_text = f'''
user {{
  email: "{email}"
  level: {level}
  account {{
    type: "xray.proxy.vless.Account"
    value: "{account_hex}"
  }}
}}
'''.lstrip()

        add_user_bin = encode_proto(
            "xray.app.proxyman.command.AddUserOperation",
            add_user_text,
            "app/proxyman/command/command.proto",
        )
        add_user_b64 = b64(add_user_bin)

        payload = (
            '{'
            f'"tag":"{settings.inbound_tag}",'
            '"operation":{'
              '"type":"xray.app.proxyman.command.AddUserOperation",'
              f'"value":"{add_user_b64}"'
            '}}'
        )

        out = run_cmd([
            settings.grpcurl_bin, "-plaintext",
            "-protoset", settings.protoset,
            "-d", payload,
            settings.xray_addr, "xray.app.proxyman.command.HandlerService/AlterInbound",
        ]).decode()
        return out

    def remove_user(self, *, email: str) -> str:
        remove_text = f'email: "{email}"\n'
        remove_bin = encode_proto(
            "xray.app.proxyman.command.RemoveUserOperation",
            remove_text,
            "app/proxyman/command/command.proto",
        )
        remove_b64 = b64(remove_bin)

        payload = (
            '{'
            f'"tag":"{settings.inbound_tag}",'
            '"operation":{'
              '"type":"xray.app.proxyman.command.RemoveUserOperation",'
              f'"value":"{remove_b64}"'
            '}}'
        )

        out = run_cmd([
            settings.grpcurl_bin, "-plaintext",
            "-protoset", settings.protoset,
            "-d", payload,
            settings.xray_addr, "xray.app.proxyman.command.HandlerService/AlterInbound",
        ]).decode()
        return out

    @staticmethod
    def is_already_exists_error(detail: str) -> bool:
        return "already exists" in (detail or "").lower()
