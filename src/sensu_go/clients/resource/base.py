# Copyright (c) 2020 XLAB Steampunk

from typing import cast, Generator, Generic, Iterable, List, Optional, Type, TypeVar

from sensu_go.clients.http.base import HTTPClient
from sensu_go.errors import ResponseError
from sensu_go.clients.resource.operator import Operator
from sensu_go.resources.base import Resource
from sensu_go.typing import JSONItem

T = TypeVar("T", bound=Resource)


class ResourceIter(Iterable[T]):
    def __init__(
        self,
        resource_class: Type[T],
        client: HTTPClient,
        path: str,
        label_selector: Optional[Operator] = None,
        field_selector: Optional[Operator] = None,
    ) -> None:
        self._resource_class = resource_class
        self._client = client
        self._path = path

        self._limit = 100

        self._query = {}
        if label_selector:
            self._query["labelSelector"] = label_selector.serialize()
        if field_selector:
            self._query["fieldSelector"] = field_selector.serialize(
                self._resource_class.FIELD_PREFIX
            )

    def __iter__(self) -> Generator[T, None, None]:
        query = dict(self._query, limit=str(self._limit))

        while True:
            resp = self._client.get(self._path, query=query)
            if resp.status != 200:
                raise ResponseError(
                    "Expected 200 when listing resources",
                    resp.url,
                    resp.status,
                    resp.text,
                )

            # TODO: Add check for invalid JSON
            data = cast(List[JSONItem], resp.json)
            for d in data:
                yield self._resource_class.from_api(self._client, d)

            query["continue"] = resp.headers.get("sensu-continue", "")
            if not query["continue"]:
                break

    def delete(self) -> None:
        for i in self:
            i.delete()


class ResourceClient(Generic[T]):
    def __init__(self, client: HTTPClient, resource_class: Type[T]) -> None:
        self._client = client
        self._resource_class = resource_class

    def _get(self, path: str) -> T:
        resp = self._client.get(path)
        if resp.status != 200:
            raise ResponseError(
                "Expected 200 when fetching resource",
                resp.url,
                resp.status,
                resp.text,
            )
        # TODO: Add check for invalid JSON
        return self._resource_class.from_api(self._client, cast(JSONItem, resp.json))

    def _find(self, path: str) -> Optional[T]:
        try:
            return self._get(path)
        except ResponseError as e:
            if e.status != 404:
                raise e
        return None

    def _delete(self, path: str) -> None:
        resp = self._client.delete(path)
        if resp.status != 204:
            raise ResponseError(
                "Expected 204 when deleting resource",
                resp.url,
                resp.status,
                resp.text,
            )

    def create(
        self,
        spec: JSONItem,
        metadata: JSONItem,
        type: Optional[str] = None,
    ) -> T:
        # We do not use POST for creating resources because not all resources support
        # this method of creation (for example, secrets and secrets providers).

        resource = self._resource_class(self._client, spec, metadata, type)
        if self._find(resource.path):
            raise ValueError("Resource at {} already exists.".format(resource.path))

        resource.save()
        return resource
