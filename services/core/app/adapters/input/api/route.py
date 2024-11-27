from pathlib import Path
from fastapi import FastAPI, Security, HTTPException, status
from fastapi.responses import FileResponse

from app.adapters.input.api.auth import User, get_user
from app.infra.config import settings


def register_base_routes(api: FastAPI):
    """Registers base api routes"""
    api.get("/download")(get_file)


async def get_file(
    name: str,
    _: User = Security(get_user, scopes=["authenticated", "file_all"]),
) -> FileResponse:
    """Returns file by his `name`."""
    path = Path(settings.storage_path).joinpath(Path(name))
    if not Path(path).is_file():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File not exist"
        )

    return FileResponse(path=path, filename=name, media_type="application/octet-stream")
