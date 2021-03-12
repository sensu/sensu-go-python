# Copyright (c) 2020 XLAB Steampunk

from typing import List, Optional, Type, TypeVar

from sensu_go.clients.http.base import HTTPClient
from sensu_go.clients.resource.base import ResourceClient
from sensu_go.resources.base import Resource
from sensu_go.resources.namespaced import NamespacedResource as NsResource
from sensu_go.typing import JSONItem

T = TypeVar("T", bound=Resource)


class NamespacedClient(ResourceClient):
    def __init__(
        self,
        client: HTTPClient,
        resource_class: Type[NsResource],
        default_namespace: str,
    ) -> None:
        super().__init__(client, resource_class)
        self._default_ns = default_namespace

    def create(
        self,
        spec: JSONItem,
        metadata: JSONItem,
        type: Optional[str] = None,
    ) -> T:
        if "namespace" not in metadata:
            metadata = dict(metadata, namespace=self._default_ns)
        return super().create(spec, metadata, type)

    def _get_path(self, ns: Optional[str], name: Optional[str] = None) -> str:
        return self.resource_class.get_path(namespace=ns or self._default_ns, name=name)

    def list(self, namespace: Optional[str] = None) -> List[NsResource]:
        return super().do_list(self._get_path(namespace))

    def find(self, name: str, namespace: Optional[str] = None) -> Optional[NsResource]:
        return self.do_find(self._get_path(namespace, name))

    def get(self, name: str, namespace: Optional[str] = None) -> NsResource:
        return super().do_get(self._get_path(namespace, name))

    def delete(self, name: str, namespace: Optional[str] = None) -> None:
        super().do_delete(self._get_path(namespace, name))
