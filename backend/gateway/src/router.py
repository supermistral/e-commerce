from fastapi import APIRouter

from .builder import APIBuilder


def get_router() -> APIRouter:
    router = APIRouter(prefix='/api/v1')

    builder = APIBuilder()
    routes = builder.build()

    print(routes)

    for route in routes:
        router.add_api_route(**route.to_dict())

    return router
