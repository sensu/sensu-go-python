# Copyright (c) 2021 XLAB Steampunk

from typing import List

from sensu_go.resources.namespaced import NamespacedResource
from sensu_go.resources.v2 import V2Mixin


class Event(V2Mixin, NamespacedResource):
    PATH_TEMPLATE = "/api/core/v2/namespaces/{namespace}/events"
    TYPE = "Event"
    API_VERSION = "core/v2"
    FIELD_PREFIX = "event"

    def validate(self) -> List[str]:
        # Events do not have names, but they need to have associated entity and a check
        # or metrics.
        result = []
        if "namespace" not in self.metadata:
            result.append("Event needs to have a namespace.")
        if "entity" not in self.spec:
            result.append("Event needs to reference an entity.")
        if not any((k in self.spec) for k in ("check", "metrics")):
            result.append("Event needs to have a check or a metrics scope.")
        return result

    @property
    def name(self) -> str:
        return "{}/{}".format(
            self.spec["entity"]["metadata"]["name"],
            self.spec["check"]["metadata"]["name"],
        )
