from core.main import create_app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(create_app(), port=5000)
