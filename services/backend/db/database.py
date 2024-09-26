from typing import Annotated
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from settings import get_settings
from sqlalchemy.orm import mapped_column, Mapped

engine = create_engine(get_settings().psql_dsn)

session = sessionmaker(engine)

intpk = Annotated[int, mapped_column(primary_key=True)]


class Base(DeclarativeBase):
    id: Mapped[intpk]
