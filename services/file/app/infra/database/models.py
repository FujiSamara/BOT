from sqlalchemy.orm import mapped_column, Mapped

from common.sql.orm import Base


class File(Base):
    __tablename__ = "files"

    name: Mapped[str] = mapped_column(nullable=False)
    ext: Mapped[str] = mapped_column(nullable=True)
    key: Mapped[str] = mapped_column(nullable=False)
    bucket: Mapped[str] = mapped_column(nullable=False)
    size: Mapped[int] = mapped_column(nullable=False)
