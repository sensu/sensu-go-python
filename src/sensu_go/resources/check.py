# Copyright (c) 2020 XLAB Steampunk

from sensu_go.clients.resource.base import ResourceIter
from sensu_go.clients.resource.operator import Equal
from sensu_go.resources.event import Event
from sensu_go.resources.namespaced import NamespacedResource
from sensu_go.resources.v2 import V2Mixin


class Check(V2Mixin, NamespacedResource):
    PATH_TEMPLATE = "/api/core/v2/namespaces/{namespace}/checks"
    TYPE = "CheckConfig"
    API_VERSION = "core/v2"
    FIELD_PREFIX = "check"

    @property
    def events(self) -> ResourceIter[Event]:
        return ResourceIter[Event](
            Event,
            self._client,
            Event.get_path(namespace=self.namespace),
            field_selector=Equal("check.name", self.name),
        )
