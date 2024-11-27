from fastapi import Security
from fastapi.routing import APIRouter

from app import services
from app.database.schemas import PostSchema

from app.adapters.input.api.auth import User, get_user


router = APIRouter()


@router.get("/by/name")
async def find_posts(
    name: str, _: User = Security(get_user, scopes=["authenticated"])
) -> list[PostSchema]:
    """Finds posts by given `name`."""
    return services.find_posts(name)
