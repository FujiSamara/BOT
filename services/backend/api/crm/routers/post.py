from fastapi import Security
from fastapi.routing import APIRouter

from db import service
from db.schemas import PostSchema

from api.auth import User, get_user


router = APIRouter()


@router.get("/by/name")
async def find_posts(
    name: str, _: User = Security(get_user, scopes=["authenticated"])
) -> list[PostSchema]:
    """Finds posts by given `name`."""
    return service.find_posts(name)
