import re
from typing import Any, Callable, Sequence, TypeVar

from .loader import GrpcLoader
from .utils import find_methods
from .mixins import ValidateMixin, CleanMixin
from .interfaces import ObjectAttrs, Servicer, GrpcTools, GrpcModel


AttrsType = TypeVar('AttrsType', bound=dict[str, str])


class GrpcParser(ValidateMixin, CleanMixin):
    """
    The protobuf parser that defines a REST API description.
    """
    __slots__ = []

    api_regex = re.compile(r'^\s*\[REST\].*')
    api_attr_regex = re.compile(r'(\w+)\s*=\s*([\w/{}\.]+)')
    api_params_regex = re.compile(r'(\w+)\s*:\s*([\w/{}]+)')

    def __init__(self) -> None:
        self.api: list[Servicer] = []
        self.loader = GrpcLoader()

    def _is_service_servicer(self, name: str) -> bool:
        return name.endswith('Servicer')

    def _is_service_stub(self, name: str) -> bool:
        return name.endswith('Stub')

    def _get_cleaned_servicer_name(self, name: str) -> str:
        """
        Cuts 'Servicer' from the end of the name
        """
        return name[:-8]

    def _get_cleaned_stub_name(self, name: str) -> str:
        """
        Cuts 'Stub' from the end of the name
        """
        return name[:-4]

    def _process_from_attrs(
        self,
        key: str,
        attrs: dict[str, str],
        handler: Callable[..., Any],
    ) -> Any:
        value = attrs.get(key, None)

        if value is None:
            return None

        return handler(value)

    def _get_api_unit_description(self, cls: type[Any], clear: bool = True) -> tuple[AttrsType, AttrsType]:
        doc = cls.__doc__ or ""
        attrs = {}
        params = {}

        lines_to_not_clear = []

        # Each line should started with "api_regex pattern"
        # After "api_regex pattern" there can be any attributes that are defined
        #   by api_attr_regex
        for line in doc.split('\n'):
            if re.search(self.api_regex, line) is None:
                if clear:
                    lines_to_not_clear.append(line)
                continue

            attrs_units = re.findall(self.api_attr_regex, line)
            params_units = re.findall(self.api_params_regex, line)
            attrs |= {k: v for k, v in attrs_units}
            params |= {k: v for k, v in params_units}

        if clear:
            cls.__doc__ = '\n'.join(lines_to_not_clear)

        return attrs, params

    def _get_api_description(self, cls: type[Any], grpc_tools: GrpcTools) -> list[ObjectAttrs]:
        methods = find_methods(cls)
        objects_to_handle: list[object] = [cls] + methods
        objects_attrs: list[ObjectAttrs] = []

        def create_model(name: str) -> GrpcModel:
            return self.loader.load_model(grpc_tools.messages[name])

        for obj in objects_to_handle:
            attrs, params = self._get_api_unit_description(obj)

            if attrs or obj is cls:
                attrs = self._validate_api_attrs(attrs)

                if obj is not cls:
                    assert 'request' in attrs
                    assert 'response' in attrs

                    request = create_model(attrs['request'])
                    response = create_model(attrs['response'])
                else:
                    request = response = None

                objects_attrs.append(ObjectAttrs(
                    obj=obj,
                    attrs=attrs,
                    params=params,
                    request=request,
                    response=response,
                ))

        return objects_attrs

    def _validate_api_attrs(self, attrs: AttrsType) -> AttrsType:
        cleaned_attrs = {}

        for k, v in attrs.items():
            validator = getattr(self, 'validate_' + k, None)
            cleaner = getattr(self, 'clean_' + k, None)

            if validator is None or validator(v):
                cleaned_attrs[k] = cleaner(v) if cleaner else v

        return cleaned_attrs

    def _parse(self, grpc_tools: GrpcTools) -> None:
        service_servicers: dict[str, type[Any]] = {}
        service_stubs: dict[str, type[Any]] = {}

        for name, cls in grpc_tools.services.items():
            if self._is_service_servicer(name):
                service_servicers[self._get_cleaned_servicer_name(name)] = cls
            elif self._is_service_stub(name):
                service_stubs[self._get_cleaned_stub_name(name)] = cls

        for cleaned_name, servicer_cls in service_servicers.items():
            stub_cls = service_stubs[cleaned_name]
            api_attrs = self._get_api_description(servicer_cls, grpc_tools=grpc_tools)

            self.api.append(Servicer(
                cls=servicer_cls,
                stub_cls=stub_cls,
                attrs=api_attrs[0],
                object_attrs=api_attrs[1:],
            ))

    def parse(self) -> Sequence[Servicer]:
        grpc_tools = self.loader.load_grpc_tools()

        for grpc_tool in grpc_tools:
            self._parse(grpc_tool)

        print(self.api)
        return self.api
