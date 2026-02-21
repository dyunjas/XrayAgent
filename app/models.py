import enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Enum, ForeignKey


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
