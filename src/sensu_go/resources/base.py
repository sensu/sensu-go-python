# Copyright (c) 2020 XLAB Steampunk

import abc
from typing import cast, List, Optional, Type, TypeVar, TYPE_CHECKING

from sensu_go.typing import JSONItem

# If we want to typecheck our code, we need to introduce a cyclic import
# ResourceClient <-> Resource. Mypy can handle such imports just fine (it does
# not run the code), but they would cause trouble during the normal operation
# of library. Do note that we also "stringified" the client type in the
# declarations below in order to avoid missing definitions during normal
# operation.
if TYPE_CHECKING:
    from sensu_go.clients.resource.base import ResourceClient

T = TypeVar("T", bound="Resource")


class Resource(metaclass=abc.ABCMeta):
    PATH_TEMPLATE: str
    TYPE: str
    API_VERSION: str

    @abc.abstractmethod
    def validate(self) -> List[str]:
        pass

    @staticmethod
    @abc.abstractmethod
    def api_to_native(data: JSONItem, type: str) -> JSONItem:
        pass

    @staticmethod
    @abc.abstractmethod
    def native_to_api(
        spec: JSONItem, metadata: JSONItem, type: str, api_version: str
    ) -> JSONItem:
        pass

    @classmethod
    def from_api(cls: Type[T], client: "ResourceClient", data: JSONItem) -> T:
        return cls(client, **cls.api_to_native(data, cls.TYPE))

    @classmethod
    def get_path(
        cls, *, namespace: Optional[str] = None, name: Optional[str] = None
    ) -> str:
        path = cls.PATH_TEMPLATE.format(namespace=namespace)
        if name:
            path += "/" + name
        return path

    def __init__(
        self,
        client: "ResourceClient",
        spec: JSONItem,
        metadata: Optional[JSONItem] = None,
        type: Optional[str] = None,
    ) -> None:
        self.client = client

        self._spec = spec
        self._metadata = metadata or {}
        self._type = type or self.TYPE

        errors = self.validate()
        if not self._type:
            errors.append("Type not set. Please specify a resource type.")
        if errors:
            raise ValueError("\n".join(errors))

    @property
    def spec(self) -> JSONItem:
        return self._spec

    @property
    def metadata(self) -> JSONItem:
        return self._metadata

    @property
    def type(self) -> str:
        return self._type

    @property
    def api_version(self) -> str:
        return self.API_VERSION

    @property
    def name(self) -> str:
        return cast(str, self.metadata["name"])

    @property
    def namespace(self) -> Optional[str]:
        return cast(Optional[str], self.metadata.get("namespace"))

    @property
    def path(self) -> str:
        return self.get_path(name=self.name, namespace=self.namespace)

    @property
    def class_path(self) -> str:
        return self.get_path(namespace=self.namespace)

    def update(self, other: "Resource") -> None:
        self._spec = other._spec
        self._metadata = other._metadata

    def to_api(self) -> JSONItem:
        return self.native_to_api(self.spec, self.metadata, self.type, self.api_version)

    def save(self) -> None:
        self.client.save(self)

    def reload(self) -> None:
        self.client.reload(self)

    def delete(self) -> None:
        self.client.do_delete(self.path)

    def __repr__(self) -> str:
        return "{}({})".format(self.type, self.path)
