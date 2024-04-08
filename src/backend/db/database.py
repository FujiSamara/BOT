from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from settings import get_settings


engine = create_async_engine(
    get_settings().psql_dsn
)

session =  async_sessionmaker(engine)

class Base(DeclarativeBase):
    pass