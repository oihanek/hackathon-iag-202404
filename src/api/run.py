from fastapi import APIRouter, FastAPI

from fraud_detection.api.routes import live
from fraud_detection.config.settings import api_settings


def generate_app():
    api_router = APIRouter()
    api_router.include_router(live.router, prefix="/live")

    app = FastAPI(
        title=api_settings.PROJECT_NAME,
        openapi_url=f"{api_settings.API_ROOT}/openapi.json",
    )

    app.include_router(api_router, prefix=api_settings.API_ROOT)
    return app


def debug():
    import uvicorn
    uvicorn.run(generate_app(), host="0.0.0.0", port=8000)


if __name__ == "__main__":
    app = generate_app()
