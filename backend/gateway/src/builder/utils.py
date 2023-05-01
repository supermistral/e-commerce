import importlib
import inspect
import sys
import re
from types import FunctionType, ModuleType
from typing import Any, Callable, Optional, TypeVar, Union

from .types import ModuleClassesType


_FuncType = TypeVar("_FuncType", bound=Callable[..., Any])


def import_module(module_name: str, file: str) -> ModuleType:
    sys.path.insert(0, file) 
    return importlib.import_module(module_name)


def import_classes(module_name: str, path: str) -> ModuleClassesType:
    module = import_module(module_name, path)
    return {k: v for k, v in inspect.getmembers(module, inspect.isclass)}


def find_methods(cls: object) -> list[Callable[..., Any]]:
    return [getattr(cls, method) for method in dir(cls)
            if callable(getattr(cls, method)) and not method.startswith('__')]


def find_class(name: str, module: ModuleType) -> Optional[type[Any]]:
    return getattr(module, name, None)


def create_annotated_function(
    f: _FuncType,
    f_types: dict[str, Union[str, type[Any]]],
    name: Optional[str]
) -> _FuncType:
    parameters = [
        inspect.Parameter(
            name=p,
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=t
        ) for p, t in f_types.items()]

    s = inspect.signature(f)
    s = s.replace(parameters=parameters)

    f.__signature__ = s
    f.__name__ = name or f.__name__

    return f


def camel_to_snake_case(s: str) -> str:
    return re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()
