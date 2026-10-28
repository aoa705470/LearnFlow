from fastapi import FastAPI

from app.core.config import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    application = FastAPI(
        title="LearnFlow API",
        version="0.1.0",
        docs_url=None if resolved_settings.app_env == "production" else "/docs",
    )
    return application


app = create_app()
