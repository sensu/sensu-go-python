# Copyright (c) 2020 XLAB Steampunk

from typing import Optional, TypeVar

from sensu_go.clients.resource.operator import Operator
from sensu_go.clients.resource.base import ResourceClient, ResourceIter
from sensu_go.resources.cluster import ClusterResource

T = TypeVar("T", bound=ClusterResource)


class ClusterClient(ResourceClient[T]):
    def list(
        self,
        label_selector: Optional[Operator] = None,
        field_selector: Optional[Operator] = None,
    ) -> ResourceIter[T]:
        return ResourceIter[T](
            self._resource_class,
            self._client,
            self._resource_class.get_path(),
            label_selector,
            field_selector,
        )

    def get(self, name: str) -> T:
        return self._get(self._resource_class.get_path(name=name))

    def find(self, name: str) -> Optional[T]:
        return self._find(self._resource_class.get_path(name=name))

    def delete(self, name: str) -> None:
        self._delete(self._resource_class.get_path(name=name))
