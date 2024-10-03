from pathlib import Path
from fastapi import FastAPI, Security, HTTPException, status
from fastapi.responses import FileResponse

from api.auth import User, authorize


def register_base_routes(api: FastAPI):
    """Registers base api routes"""
    api.get("/download")(download_file)


async def download_file(
    path: str, _: User = Security(authorize, scopes=["authenticated"])
) -> FileResponse:
    """Returns file by his `path`."""
    if not Path(path).is_file():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File not exist"
        )

    filename = Path(path).name

    return FileResponse(
        path=path, filename=filename, media_type="application/octet-stream"
    )
