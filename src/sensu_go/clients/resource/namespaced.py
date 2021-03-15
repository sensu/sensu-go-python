# Copyright (c) 2020 XLAB Steampunk

from typing import Optional, Type, TypeVar

from sensu_go.clients.http.base import HTTPClient
from sensu_go.clients.resource.base import ResourceClient, ResourceIter
from sensu_go.clients.resource.operator import Operator
from sensu_go.resources.namespaced import NamespacedResource
from sensu_go.typing import JSONItem

T = TypeVar("T", bound=NamespacedResource)


class NamespacedClient(ResourceClient[T]):
    def __init__(
        self,
        client: HTTPClient,
        resource_class: Type[T],
        default_namespace: str,
    ) -> None:
        super().__init__(client, resource_class)
        self._default_ns = default_namespace

    def _get_path(self, ns: Optional[str], name: Optional[str] = None) -> str:
        return self._resource_class.get_path(
            namespace=ns or self._default_ns, name=name
        )

    def list(
        self,
        namespace: Optional[str] = None,
        label_selector: Optional[Operator] = None,
        field_selector: Optional[Operator] = None,
    ) -> ResourceIter[T]:
        return ResourceIter[T](
            self._resource_class,
            self._client,
            self._get_path(namespace),
            label_selector,
            field_selector,
        )

    def create(
        self,
        spec: JSONItem,
        metadata: JSONItem,
        type: Optional[str] = None,
    ) -> T:
        if "namespace" not in metadata:
            metadata = dict(metadata, namespace=self._default_ns)
        return super().create(spec, metadata, type)

    def get(self, name: str, namespace: Optional[str] = None) -> T:
        return self._get(self._get_path(namespace, name))

    def find(self, name: str, namespace: Optional[str] = None) -> Optional[T]:
        return self._find(self._get_path(namespace, name))

    def delete(self, name: str, namespace: Optional[str] = None) -> None:
        self._delete(self._get_path(namespace, name))
