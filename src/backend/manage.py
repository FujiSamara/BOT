from core.main import create_app
import uvicorn
from configure import configure
from settings import get_settings

def run():
    configure()
    get_settings()
    uvicorn.run(create_app(), port=5000)

if __name__ == "__main__":
    run()