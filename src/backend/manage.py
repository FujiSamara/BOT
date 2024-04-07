import uvicorn
from configure import configure
from settings import get_settings
from core.main import create_app


def run():
    configure()
    get_settings()
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    uvicorn.run(create_app(), port=5000, log_config=log_config)

if __name__ == "__main__":
    run()