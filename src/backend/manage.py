import uvicorn
from configure import configure
import pathlib


def run():
    configure()
    
    from core.main import create_app
    log_config_path = (pathlib.Path(__file__).parent / 'log_config.yaml').resolve().as_posix()
    uvicorn.run(create_app(), host='0.0.0.0', port=5200, log_config=log_config_path)

if __name__ == "__main__":
    run()