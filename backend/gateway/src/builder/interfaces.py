from dataclasses import dataclass, asdict
from typing import Optional, Callable, Any

from google.protobuf.message import Message
from pydantic import BaseModel

from .types import ModuleClassesType


@dataclass(frozen=True)
class GrpcTools:
    services: ModuleClassesType
    messages: ModuleClassesType


@dataclass(frozen=True)
class GrpcModel:
    cls: type[Message]
    model: type[BaseModel]


@dataclass(frozen=True)
class ObjectAttrs:
    obj: type[Any]
    attrs: dict[str, str]
    params: dict[str, str]
    request: Optional[GrpcModel] = None
    response: Optional[GrpcModel] = None


@dataclass(frozen=True)
class Servicer:
    cls: type[Any]
    stub_cls: type[Any]
    attrs: ObjectAttrs
    object_attrs: list[ObjectAttrs]


@dataclass(frozen=True)
class RouteAttrs:
    path: str
    endpoint: Callable[..., Any]
    methods: list[str]
    response_model: Optional[type[BaseModel]] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
