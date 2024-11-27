from fastapi import Security
from fastapi.routing import APIRouter

from app.db import service
from app.db.schemas import PostSchema

from app.api.auth import User, get_user


router = APIRouter()


@router.get("/by/name")
async def find_posts(
    name: str, _: User = Security(get_user, scopes=["authenticated"])
) -> list[PostSchema]:
    """Finds posts by given `name`."""
    return service.find_posts(name)
