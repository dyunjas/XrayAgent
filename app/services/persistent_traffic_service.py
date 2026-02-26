from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock

from sqlalchemy.orm import Session

from app.config import settings


class PersistentTrafficService:
    def __init__(self):
        self._table_ready = False
        self._lock = RLock()
        self._db_path = Path(settings.traffic_sqlite_path).expanduser()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._db_path), timeout=30)
        conn.row_factory = sqlite3.Row
        return conn

    def ensure_table(self, db: Session | None = None) -> None:
        if self._table_ready:
            return

        with self._lock:
            if self._table_ready:
                return

            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            with self._connect() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS vpn_user_traffic_snapshot (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        server_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        email TEXT NOT NULL DEFAULT '',
                        last_uplink INTEGER NOT NULL DEFAULT 0,
                        last_downlink INTEGER NOT NULL DEFAULT 0,
                        total_uplink INTEGER NOT NULL DEFAULT 0,
                        total_downlink INTEGER NOT NULL DEFAULT 0,
                        updated_at TEXT NOT NULL,
                        UNIQUE(server_id, user_id)
                    )
                    """
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS ix_vpn_user_traffic_snapshot_server_id ON vpn_user_traffic_snapshot(server_id)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS ix_vpn_user_traffic_snapshot_user_id ON vpn_user_traffic_snapshot(user_id)"
                )
                conn.commit()

            self._table_ready = True

    def apply_snapshot(
        self,
        db: Session,
        *,
        server_id: int,
        user_id: int,
        email: str,
        current_uplink: int,
        current_downlink: int,
    ) -> dict[str, int]:
        self.ensure_table(db)

        now = datetime.now(timezone.utc).isoformat()
        cur_up = max(0, int(current_uplink or 0))
        cur_down = max(0, int(current_downlink or 0))

        with self._lock:
            with self._connect() as conn:
                row = conn.execute(
                    """
                    SELECT last_uplink, last_downlink, total_uplink, total_downlink
                    FROM vpn_user_traffic_snapshot
                    WHERE server_id = ? AND user_id = ?
                    """,
                    (int(server_id), int(user_id)),
                ).fetchone()

                if row is None:
                    conn.execute(
                        """
                        INSERT INTO vpn_user_traffic_snapshot (
                            server_id, user_id, email, last_uplink, last_downlink,
                            total_uplink, total_downlink, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            int(server_id),
                            int(user_id),
                            email,
                            cur_up,
                            cur_down,
                            cur_up,
                            cur_down,
                            now,
                        ),
                    )
                    conn.commit()
                    return {
                        "uplink": cur_up,
                        "downlink": cur_down,
                        "total": cur_up + cur_down,
                    }

                prev_up = max(0, int(row["last_uplink"] or 0))
                prev_down = max(0, int(row["last_downlink"] or 0))
                total_up = max(0, int(row["total_uplink"] or 0))
                total_down = max(0, int(row["total_downlink"] or 0))

                # Counter reset after xray/service restart: take current value as new delta.
                delta_up = cur_up - prev_up if cur_up >= prev_up else cur_up
                delta_down = cur_down - prev_down if cur_down >= prev_down else cur_down

                total_up += max(0, delta_up)
                total_down += max(0, delta_down)

                conn.execute(
                    """
                    UPDATE vpn_user_traffic_snapshot
                    SET email = ?,
                        last_uplink = ?,
                        last_downlink = ?,
                        total_uplink = ?,
                        total_downlink = ?,
                        updated_at = ?
                    WHERE server_id = ? AND user_id = ?
                    """,
                    (
                        email,
                        cur_up,
                        cur_down,
                        total_up,
                        total_down,
                        now,
                        int(server_id),
                        int(user_id),
                    ),
                )
                conn.commit()

                return {
                    "uplink": total_up,
                    "downlink": total_down,
                    "total": total_up + total_down,
                }

    def get_totals(self, db: Session, *, server_id: int, user_id: int) -> dict[str, int]:
        self.ensure_table(db)

        with self._lock:
            with self._connect() as conn:
                row = conn.execute(
                    """
                    SELECT total_uplink, total_downlink
                    FROM vpn_user_traffic_snapshot
                    WHERE server_id = ? AND user_id = ?
                    """,
                    (int(server_id), int(user_id)),
                ).fetchone()

        if row is None:
            return {"uplink": 0, "downlink": 0, "total": 0}

        uplink = int(row["total_uplink"] or 0)
        downlink = int(row["total_downlink"] or 0)
        return {"uplink": uplink, "downlink": downlink, "total": uplink + downlink}

    def reset_users(self, db: Session, *, server_id: int, user_ids: list[int] | None = None) -> int:
        self.ensure_table(db)

        with self._lock:
            with self._connect() as conn:
                if user_ids:
                    placeholders = ",".join("?" for _ in user_ids)
                    query = (
                        "UPDATE vpn_user_traffic_snapshot "
                        "SET last_uplink = 0, last_downlink = 0, total_uplink = 0, total_downlink = 0, updated_at = ? "
                        f"WHERE server_id = ? AND user_id IN ({placeholders})"
                    )
                    params = [datetime.now(timezone.utc).isoformat(), int(server_id), *[int(uid) for uid in user_ids]]
                else:
                    query = (
                        "UPDATE vpn_user_traffic_snapshot "
                        "SET last_uplink = 0, last_downlink = 0, total_uplink = 0, total_downlink = 0, updated_at = ? "
                        "WHERE server_id = ?"
                    )
                    params = [datetime.now(timezone.utc).isoformat(), int(server_id)]

                cur = conn.execute(query, params)
                conn.commit()
                return int(cur.rowcount or 0)

    def apply_snapshots_bulk(
        self,
        db: Session,
        *,
        server_id: int,
        snapshots: list[dict],
    ) -> dict[int, dict[str, int]]:
        self.ensure_table(db)
        if not snapshots:
            return {}

        result: dict[int, dict[str, int]] = {}
        now = datetime.now(timezone.utc).isoformat()
        user_ids = [int(item["user_id"]) for item in snapshots]

        with self._lock:
            with self._connect() as conn:
                placeholders = ",".join("?" for _ in user_ids)
                existing_rows = conn.execute(
                    f"""
                    SELECT server_id, user_id, email, last_uplink, last_downlink, total_uplink, total_downlink
                    FROM vpn_user_traffic_snapshot
                    WHERE server_id = ? AND user_id IN ({placeholders})
                    """,
                    [int(server_id), *user_ids],
                ).fetchall()
                by_user_id = {int(row["user_id"]): row for row in existing_rows}

                for item in snapshots:
                    uid = int(item["user_id"])
                    email = str(item.get("email") or "")
                    cur_up = max(0, int(item.get("current_uplink", 0) or 0))
                    cur_down = max(0, int(item.get("current_downlink", 0) or 0))
                    available = bool(item.get("available"))
                    row = by_user_id.get(uid)

                    if row is None:
                        conn.execute(
                            """
                            INSERT INTO vpn_user_traffic_snapshot (
                                server_id, user_id, email, last_uplink, last_downlink,
                                total_uplink, total_downlink, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                int(server_id),
                                uid,
                                email,
                                cur_up,
                                cur_down,
                                cur_up,
                                cur_down,
                                now,
                            ),
                        )
                        result[uid] = {
                            "uplink": cur_up,
                            "downlink": cur_down,
                            "total": cur_up + cur_down,
                        }
                        continue

                    last_up = max(0, int(row["last_uplink"] or 0))
                    last_down = max(0, int(row["last_downlink"] or 0))
                    total_up = max(0, int(row["total_uplink"] or 0))
                    total_down = max(0, int(row["total_downlink"] or 0))

                    next_last_up = last_up
                    next_last_down = last_down
                    if available:
                        delta_up = cur_up - last_up if cur_up >= last_up else cur_up
                        delta_down = cur_down - last_down if cur_down >= last_down else cur_down
                        total_up += max(0, delta_up)
                        total_down += max(0, delta_down)
                        next_last_up = cur_up
                        next_last_down = cur_down

                    conn.execute(
                        """
                        UPDATE vpn_user_traffic_snapshot
                        SET email = ?,
                            last_uplink = ?,
                            last_downlink = ?,
                            total_uplink = ?,
                            total_downlink = ?,
                            updated_at = ?
                        WHERE server_id = ? AND user_id = ?
                        """,
                        (
                            email,
                            next_last_up,
                            next_last_down,
                            total_up,
                            total_down,
                            now,
                            int(server_id),
                            uid,
                        ),
                    )

                    result[uid] = {
                        "uplink": total_up,
                        "downlink": total_down,
                        "total": total_up + total_down,
                    }

                conn.commit()

        return result
