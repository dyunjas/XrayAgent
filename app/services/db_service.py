from sqlalchemy import text
from sqlalchemy.orm import Session


class DBService:
    def db_health(self, db: Session) -> dict:
        try:
            one = db.execute(text("SELECT 1")).scalar_one()
            return {"ok": True, "result": int(one)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def active_keys_count(self, db: Session, *, server_id: int) -> dict:
        try:
            cnt = db.execute(
                text("SELECT count(*) FROM vpn_keys WHERE status='active' AND server_id=:sid")
                .bindparams(sid=server_id)
            ).scalar_one()
            return {"ok": True, "active_keys": int(cnt), "server_id": int(server_id)}
        except Exception as e:
            return {"ok": False, "error": str(e)}
