from db.database import Base, engine
from db.models import *

def create_tables():
    Base.metadata.create_all(engine)