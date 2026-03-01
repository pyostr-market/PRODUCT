import uvicorn

from src.core.conf.settings import get_settings

settings = get_settings()


if __name__ == "__main__":
    uvicorn.run(
        "src.mount:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="debug",
    )