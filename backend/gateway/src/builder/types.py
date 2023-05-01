from typing import Any, TypeVar

from pydantic import BaseModel


ModuleClassesType = TypeVar('ModuleClassesType', bound=dict[str, type[Any]])

APIModelType = TypeVar('APIModelType', bound=type[BaseModel])
