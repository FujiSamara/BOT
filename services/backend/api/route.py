from pathlib import Path
from fastapi import FastAPI, Security, HTTPException, status
from fastapi.responses import FileResponse

from api.auth import User, get_user, UserWithScopes
from settings import get_settings


def register_base_routes(api: FastAPI):
    """Registers base api routes"""
    api.get("/download")(get_file)


async def get_file(
    name: str,
    _: User = Security(get_user, scopes=["authenticated", "file_all"]),
) -> FileResponse:
    """Returns file by his `name`."""
    path = Path.joinpath(get_settings().storage_path, name)
    if not Path(path).is_file():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File not exist"
        )

    return FileResponse(path=path, filename=name, media_type="application/octet-stream")


async def get_allowed_files(
    name: str,
    user: UserWithScopes = Security(get_user, scopes=["authenticated", "file_all"]),
) -> FileResponse:
    pass
