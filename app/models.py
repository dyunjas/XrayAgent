import enum
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Enum, ForeignKey, BigInteger, DateTime, UniqueConstraint


class Base(DeclarativeBase):
    pass


class KeyStatus(str, enum.Enum):
    active = "active"
    deleted = "deleted"


class Key(Base):
    __tablename__ = "vpn_keys"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column()
    server_id: Mapped[int] = mapped_column(ForeignKey("vpn_servers.id", ondelete="CASCADE"))

    uuid: Mapped[str] = mapped_column(String(36), unique=True)
    uri: Mapped[str | None] = mapped_column(nullable=True)
    status: Mapped[KeyStatus] = mapped_column(Enum(KeyStatus), default=KeyStatus.active)


class UserTrafficSnapshot(Base):
    __tablename__ = "vpn_user_traffic_snapshot"
    __table_args__ = (
        UniqueConstraint("server_id", "user_id", name="uq_vpn_user_traffic_snapshot_server_user"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    server_id: Mapped[int] = mapped_column(index=True)
    user_id: Mapped[int] = mapped_column(index=True)
    email: Mapped[str] = mapped_column(String(255), default="")

    last_uplink: Mapped[int] = mapped_column(BigInteger, default=0)
    last_downlink: Mapped[int] = mapped_column(BigInteger, default=0)
    total_uplink: Mapped[int] = mapped_column(BigInteger, default=0)
    total_downlink: Mapped[int] = mapped_column(BigInteger, default=0)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
