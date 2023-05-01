import uvicorn
from fastapi import FastAPI

from .config import settings
from .router import get_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_TITLE,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.PROJECT_VERSION,
    )

    router = get_router()
    app.include_router(router)

    return app


app = create_app()


if __name__ == '__main__':
    uvicorn.run('main:app', port=settings.HOST_PORT, reload=True)
