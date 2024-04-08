from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


engine = create_async_engine(
    # TODO: make psql url
)

session =  async_sessionmaker(engine)

class Base(DeclarativeBase):
    pass