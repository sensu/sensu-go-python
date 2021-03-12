# Copyright (c) 2020 XLAB Steampunk

from typing import List, Optional

from sensu_go.clients.resource.base import ResourceClient
from sensu_go.resources.cluster import ClusterResource


class ClusterClient(ResourceClient):
    def list(self) -> List[ClusterResource]:
        return super().do_list(self.resource_class.get_path())

    def find(self, name: str) -> Optional[ClusterResource]:
        return self.do_find(self.resource_class.get_path(name=name))

    def get(self, name: str) -> ClusterResource:
        return super().do_get(self.resource_class.get_path(name=name))

    def delete(self, name: str) -> None:
        super().do_delete(self.resource_class.get_path(name=name))
