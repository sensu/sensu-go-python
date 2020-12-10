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


class Resource(JSONItem, metaclass=abc.ABCMeta):
    PATH_TEMPLATE: str

    @staticmethod
    @abc.abstractmethod
    def validate(data: JSONItem) -> List[str]:
        pass

    @staticmethod
    @abc.abstractmethod
    def api_to_native(data: JSONItem) -> JSONItem:
        pass

    @staticmethod
    @abc.abstractmethod
    def native_to_api(data: JSONItem) -> JSONItem:
        pass

    @classmethod
    def from_api(cls: Type[T], client: "ResourceClient", data: JSONItem) -> T:
        return cls(client, cls.api_to_native(data))

    @classmethod
    def get_path(
        cls, *, namespace: Optional[str] = None, name: Optional[str] = None
    ) -> str:
        path = cls.PATH_TEMPLATE.format(namespace=namespace)
        return path + "/" + name if name else path

    def __init__(self, client: "ResourceClient", data: JSONItem) -> None:
        errors = self.validate(data)
        if errors:
            raise ValueError("\n".join(errors))

        super().__init__(data)
        self.client = client

    @property
    def name(self) -> str:
        return cast(str, self["metadata"]["name"])

    @property
    def namespace(self) -> Optional[str]:
        return cast(Optional[str], self.get("metadata", {}).get("namespace"))

    @property
    def path(self) -> str:
        return self.get_path(name=self.name, namespace=self.namespace)

    def to_api(self) -> JSONItem:
        return self.native_to_api(self)

    def save(self) -> None:
        self.client.save(self)

    def reload(self) -> None:
        self.client.reload(self)

    def delete(self) -> None:
        self.client.do_delete(self.path)
