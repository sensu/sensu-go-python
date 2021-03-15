# Copyright (c) 2020 XLAB Steampunk

from typing import List, Optional

from sensu_go.clients.resource.operator import Operator
from sensu_go.clients.resource.base import ResourceClient
from sensu_go.resources.cluster import ClusterResource


class ClusterClient(ResourceClient):
    def list(
        self,
        label_selector: Optional[Operator] = None,
        field_selector: Optional[Operator] = None,
    ) -> List[ClusterResource]:
        return self.do_list(
            self.resource_class.get_path(),
            label_selector=label_selector,
            field_selector=field_selector,
        )

    def get(self, name: str) -> T:
        return self._get(self._resource_class.get_path(name=name))

    def find(self, name: str) -> Optional[T]:
        return self._find(self._resource_class.get_path(name=name))

    def delete(self, name: str) -> None:
        self._delete(self._resource_class.get_path(name=name))
