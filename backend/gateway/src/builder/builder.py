from typing import Any, Callable, Sequence

from grpc import aio as grpc

from .loader import GrpcLoader
from .interfaces import GrpcModel, ObjectAttrs, RouteAttrs, Servicer
from .utils import camel_to_snake_case, create_annotated_function
from .parser import GrpcParser


class APIBuilder:
    """
    The API builder that acts according to protobuf description. 
    It uses `GrpcParser` to parse existing files and after that creates
    interface instance with params for the `fastapi.APIRouter`
    """
    __slots__ = ['parser']

    def __init__(self) -> None:
        self.parser = GrpcParser()

    def _get_path(self, attrs: ObjectAttrs) -> str:
        path = attrs.attrs.get('path', None) or (f'/{attrs.obj.__name__}/')
        return path

    def _get_service_path(self, attrs: ObjectAttrs) -> str:
        path = attrs.attrs.get('path', None) or attrs.obj.__name__.rstrip('Servicer')
        return path.rstrip('/')

    def _build_service_route(self, servicer: Servicer) -> list[RouteAttrs]:
        servicer_attrs = servicer.attrs
        service_path = self._get_service_path(servicer_attrs)

        assert 'host' in servicer_attrs.attrs
        assert 'port' in servicer_attrs.attrs

        host, port = servicer_attrs.attrs['host'], servicer_attrs.attrs['port']

        channel = grpc.insecure_channel(f'{host}:{port}')
        stub = servicer.stub_cls(channel)

        def endpoint_builder(
            name: str,
            params: dict[str, str],
            request_model: GrpcModel,
            response_model: GrpcModel,
        ) -> Callable[..., Any]:
            procedure = getattr(stub, name)

            async def endpoint(**kwargs) -> Any:
                request = kwargs.get('request')
                response_msg = await procedure(
                    GrpcLoader.model_to_message(
                        model=request,
                        message=request_model.cls
                    )
                )
                return GrpcLoader.message_to_model(
                    message=response_msg,
                    model=response_model.model
                )

            return create_annotated_function(
                endpoint,
                params,
                name=camel_to_snake_case(name)
            )

        routes = []

        for attrs in servicer.object_attrs:
            path = service_path + self._get_path(attrs)
            endpoint = endpoint_builder(
                name=attrs.obj.__name__,
                params=attrs.params | {'request': attrs.request.model},
                request_model=attrs.request,
                response_model=attrs.response,
            )

            routes.append(RouteAttrs(
                path=path,
                endpoint=endpoint,
                methods=[attrs.attrs.get('method')],
                response_model=attrs.response.model,
            ))

        return routes

    def build(self) -> Sequence[RouteAttrs]:
        servicers = self.parser.parse()
        routes = []

        for servicer in servicers:
            routes += self._build_service_route(servicer)

        return routes

