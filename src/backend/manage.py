import uvicorn
from configure import configure
from core.main import create_app
from settings import get_settings


def run():
    configure()
    
    log_config_path = get_settings().app_directory_path + '/log_config.yaml'
    uvicorn.run(
        app=create_app(), 
        host=get_settings().host, 
        port=get_settings().port, 
        log_config=log_config_path,
        ssl_keyfile=get_settings().ssl_keyfile,
        ssl_certfile=get_settings().ssl_certfile
    )

if __name__ == "__main__":
    run()