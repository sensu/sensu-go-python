# Copyright (c) 2020 XLAB Steampunk

from typing import cast, List

from sensu_go.resources.cluster import ClusterResource
from sensu_go.resources.v2 import V2Mixin
from sensu_go.typing import JSONItem


class Namespace(V2Mixin, ClusterResource):
    PATH_TEMPLATE = "/api/core/v2/namespaces"

    @staticmethod
    def validate(data: JSONItem) -> List[str]:
        result = []
        if not data.get("name"):
            result.append("Namespace needs to have a 'name'.")
        return result

    @property
    def name(self) -> str:
        return cast(str, self["name"])
