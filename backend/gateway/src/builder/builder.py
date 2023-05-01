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

    def _validate_servicer(self, servicer: Servicer) -> None:
        assert 'host' in servicer.attrs.attrs
        assert 'port' in servicer.attrs.attrs

        for method in servicer.object_attrs:
            self._validate_grpc_method(method)

    def _validate_grpc_method(self, method: ObjectAttrs) -> None:
        assert all(key in method.request.cls.DESCRIPTOR.fields_by_name
                   for key in method.params.keys())

    def _create_endpoint(
        self,
        stub: Any,
        name: str,
        params: dict[str, str],
        request_model: GrpcModel,
        response_model: GrpcModel,
    ) -> Callable[..., Any]:
        procedure = getattr(stub, name)

        async def endpoint(**kwargs) -> Any:
            request = kwargs.get('request')
            response = await procedure(
                GrpcLoader.model_to_message(
                    model=request,
                    message=request_model.cls,
                    fields={k: kwargs.get(k) for k in params.keys()}
                )
            )
            return GrpcLoader.message_to_model(
                message=response,
                model=response_model.model
            )

        # Exclude params keys from the model to ensure the key exists
        # either as a path variable or in the body
        _request_model = GrpcLoader.exclude_model_fields(
            model=request_model.model,
            fields=params.keys()
        )

        # Add 'request' param to the endpoint function as a body
        # Don't add 'request' argument of 'Body' type from the endpoint
        #   if it's empty
        if _request_model.__fields__:
            # not '|=' operator cause there shouldn't be side effect
            params = params | {'request': _request_model}

        return create_annotated_function(
            endpoint,
            params,
            name=camel_to_snake_case(name)
        )

    def _build_service_route(self, servicer: Servicer) -> list[RouteAttrs]:
        servicer_attrs = servicer.attrs
        service_path = self._get_service_path(servicer_attrs)

        host, port = servicer_attrs.attrs['host'], servicer_attrs.attrs['port']

        channel = grpc.insecure_channel(f'{host}:{port}')
        stub = servicer.stub_cls(channel)

        routes = []

        for attrs in servicer.object_attrs:
            path = service_path + self._get_path(attrs)
            endpoint = self._create_endpoint(
                stub=stub,
                name=attrs.obj.__name__,
                params=attrs.params,
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
            self._validate_servicer(servicer)

            routes += self._build_service_route(servicer)

        return routes

