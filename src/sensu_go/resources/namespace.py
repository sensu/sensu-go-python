# Copyright (c) 2020 XLAB Steampunk

from typing import cast, List

from sensu_go.resources.cluster import ClusterResource
from sensu_go.typing import JSONItem


class Namespace(ClusterResource):
    PATH_TEMPLATE = "/api/core/v2/namespaces"
    TYPE = "Namespace"
    API_VERSION = "core/v2"
    FIELD_PREFIX = "namespace"

    @staticmethod
    def api_to_native(data: JSONItem, type: str) -> JSONItem:
        return dict(metadata={}, spec=data, type=type)

    @staticmethod
    def native_to_api(
        spec: JSONItem, metadata: JSONItem, type: str, api_version: str
    ) -> JSONItem:
        return spec

    def validate(self) -> List[str]:
        result = []
        if not self.spec.get("name"):
            result.append("Namespace needs to have a 'name'.")
        return result

    @property
    def name(self) -> str:
        return cast(str, self.spec["name"])
