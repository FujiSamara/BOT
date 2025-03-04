import uvicorn

from common.logging import config, logger
from common.config import generate

from app.infra.config import Settings
from app import app


def run():
    settings = generate(Settings, logger)

    uvicorn.run(
        app=app,
        host=settings.host,
        port=settings.port,
        log_config=config,
        ssl_keyfile=settings.ssl_keyfile,
        ssl_certfile=settings.ssl_certfile,
        root_path=settings.root_path,
    )


if __name__ == "__main__":
    run()
