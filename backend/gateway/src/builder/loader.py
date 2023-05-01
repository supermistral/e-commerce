import re
from collections import defaultdict
from typing import Any, Generator, TypeVar

from protobuf_to_pydantic import msg_to_pydantic_model
from google.protobuf.json_format import MessageToDict, ParseDict
from google.protobuf.message import Message
from pydantic import BaseModel

from .utils import import_classes
from .interfaces import GrpcTools, GrpcModel
from .types import ModuleClassesType
from ..config import settings


APIModelType = TypeVar('APIModelType', bound=BaseModel)


class GrpcLoader:
    """
    The loader of generated modules: containing servicers and stubs, messages
    and models. It's also responsible for the generation of models.
    """
    __slots__ = ['models_cache']

    grpc_tools_regex = re.compile(r'_(pb2(_grpc)?)')
    grpc_tools_args = {'pb2': 'messages',
                       'pb2_grpc': 'services'}

    def __init__(self) -> None:
        self.models_cache: dict[str, type[APIModelType]] = {}

    def _import_classes_by_tool(self, tool: str, **kwargs) -> tuple[str, ModuleClassesType]:
        arg_name = self.grpc_tools_args[tool]
        return arg_name, import_classes(**kwargs)

    def load_grpc_tools(self) -> Generator[GrpcTools, None, None]:
        grpc_files = list(settings.GRPC_TOOLS_DIR.glob(f'**/*.py'))
        grouped_grpc_files = defaultdict(dict)

        # Group by parent directory
        for file in grpc_files:
            tool = re.search(self.grpc_tools_regex, str(file))

            if tool is None:
                continue

            tool = tool.group(1)
            parent = file.parent.name

            # Parse file path
            # e.g. /path/to/proto/dir/service/grpc.py
            # path = /path/to/proto/dir
            # module name = service.grpc
            path = str(file.parent.parent)
            module_name = f"{file.parent.name}.{file.stem}"

            grouped_grpc_files[parent][tool] = {
                'module_name': module_name,
                'path': path,
            }

        for tools in grouped_grpc_files.values():
            tools_args = [self._import_classes_by_tool(k, **v)
                            for k, v in tools.items()]
            yield GrpcTools(**dict(tools_args))

    def load_model(self, cls: type[Any]) -> GrpcModel:
        name = cls.__name__

        if name in self.models_cache:
            return self.models_cache[name]

        self.models_cache[name] = GrpcModel(
            cls=cls,
            model=msg_to_pydantic_model(cls)
        )

        return self.models_cache[name]

    @staticmethod
    def message_to_model(message: Message, model: type[APIModelType]) -> APIModelType:
        dict = MessageToDict(message)
        return model.parse_obj(dict)

    @staticmethod
    def model_to_message(model: APIModelType, message: type[Message]) -> Message:
        return ParseDict(model.dict(), message())
