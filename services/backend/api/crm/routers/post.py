from fastapi import Security
from fastapi.routing import APIRouter

from db import service
from db.schemas import PostSchema

from api.auth import User, authorize


router = APIRouter()


@router.get("/by/name")
async def find_posts(
    name: str, _: User = Security(authorize, scopes=["authenticated"])
) -> list[PostSchema]:
    """Finds posts by given `name`."""
    return service.find_posts(name)
