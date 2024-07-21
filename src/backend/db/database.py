from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from settings import get_settings


engine = create_engine(get_settings().psql_dsn)

session = sessionmaker(engine)


class Base(DeclarativeBase):
    pass
