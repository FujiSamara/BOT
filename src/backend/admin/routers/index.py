from fastapi.routing import APIRouter

index = APIRouter()


@index.get('/')
async def hello():
    return "Hello world!"