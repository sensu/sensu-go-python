# Copyright (c) 2020 XLAB Steampunk

import abc
from typing import cast, List, Optional, Type, TypeVar

from sensu_go.clients.http.base import HTTPClient
from sensu_go.errors import ResponseError
from sensu_go.typing import JSONItem

T = TypeVar("T", bound="Resource")


class Resource(metaclass=abc.ABCMeta):
    PATH_TEMPLATE: str
    TYPE: str
    API_VERSION: str
    FIELD_PREFIX: str

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
    def from_api(cls: Type[T], client: HTTPClient, data: JSONItem) -> T:
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
        client: HTTPClient,
        spec: JSONItem,
        metadata: JSONItem,
        type: Optional[str] = None,
    ) -> None:
        self._client = client

        self._spec = spec
        self._metadata = metadata

        # Type is optional if the derived class provides it.
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

    def save(self) -> None:
        resp = self._client.put(
            self.path,
            self.native_to_api(self.spec, self.metadata, self.type, self.api_version),
        )
        if resp.status not in (200, 201):
            raise ResponseError(
                "Expected 200 or 201 when updating resource",
                resp.url,
                resp.status,
                resp.text,
            )

        # We need to reload the resource because the backend can add some
        # default values on top of what we sent.
        self.reload()

    def reload(self) -> None:
        resp = self._client.get(self.path)
        if resp.status != 200:
            raise ResponseError(
                "Expected 200 when fetching resource",
                resp.url,
                resp.status,
                resp.text,
            )
        native = self.api_to_native(cast(JSONItem, resp.json), self.type)
        self._spec = native["spec"]
        self._metadata = native["metadata"]

    def delete(self) -> None:
        resp = self._client.delete(self.path)
        if resp.status != 204:
            raise ResponseError(
                "Expected 204 when deleting resource",
                resp.url,
                resp.status,
                resp.text,
            )

    def __repr__(self) -> str:
        return "{}({})".format(self.type, self.path)
