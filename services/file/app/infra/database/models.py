from datetime import datetime
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import UniqueConstraint

from common.sql.orm import Base


class File(Base):
    __tablename__ = "files"

    name: Mapped[str] = mapped_column(nullable=False)
    ext: Mapped[str] = mapped_column(nullable=True)
    key: Mapped[str] = mapped_column(nullable=False)
    bucket: Mapped[str] = mapped_column(nullable=False)
    size: Mapped[int] = mapped_column(nullable=False)
    created: Mapped[datetime] = mapped_column(nullable=False)
    confirmed: Mapped[bool] = mapped_column(nullable=False, default=False)

    __table_args__ = (UniqueConstraint("key", "bucket", name="uq_key_bucket"),)
