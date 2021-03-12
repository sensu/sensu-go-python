# Copyright (c) 2020 XLAB Steampunk

from typing import cast, List, Optional, Type, TypeVar

from sensu_go.clients.http.base import HTTPClient
from sensu_go.errors import ResponseError
from sensu_go.resources.base import Resource
from sensu_go.typing import JSONItem

T = TypeVar("T", bound=Resource)


class ResourceClient:
    def __init__(self, client: HTTPClient, resource_class: Type[T]) -> None:
        self.client = client
        self.resource_class = resource_class

    def do_list(self, path: str) -> List[T]:
        resp = self.client.get(path)
        if resp.status != 200:
            raise ResponseError(
                "Expected 200 when listing resources",
                resp.url,
                resp.status,
                resp.text,
            )
        # TODO: Add check for invalid JSON
        data = cast(List[JSONItem], resp.json)
        return [self.resource_class.from_api(self, d) for d in data]

    def do_find(self, path: str) -> Optional[T]:
        resp = self.client.get(path)
        if resp.status == 404:
            return None

        if resp.status != 200:
            raise ResponseError(
                "Expected 200 when fetching resource",
                resp.url,
                resp.status,
                resp.text,
            )
        # TODO: Add check for invalid JSON
        return self.resource_class.from_api(self, cast(JSONItem, resp.json))

    def do_get(self, path: str) -> T:
        resp = self.client.get(path)
        if resp.status != 200:
            raise ResponseError(
                "Expected 200 when fetching resource",
                resp.url,
                resp.status,
                resp.text,
            )
        # TODO: Add check for invalid JSON
        return self.resource_class.from_api(self, cast(JSONItem, resp.json))

    def do_delete(self, path: str) -> None:
        resp = self.client.delete(path)
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
        resource = self.resource_class(self, spec, metadata, type)
        resp = self.client.post(resource.class_path, resource.to_api())
        if resp.status != 201:
            raise ResponseError(
                "Expected 201 when creating resource",
                resp.url,
                resp.status,
                resp.text,
            )

        # We need to reload the resource because the backend can add some
        # default values on top of what we sent.
        self.reload(resource)

        return resource

    def save(self, resource: T) -> None:
        resp = self.client.put(resource.path, resource.to_api())
        if resp.status not in (200, 201):
            raise ResponseError(
                "Expected 200 or 201 when updating resource",
                resp.url,
                resp.status,
                resp.text,
            )

        # We need to reload the resource because the backend can add some
        # default values on top of what we sent.
        self.reload(resource)

    def reload(self, resource: T) -> None:
        resource.update(cast(T, self.do_get(resource.path)))
