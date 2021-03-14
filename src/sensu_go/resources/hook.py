# Copyright (c) 2020 XLAB Steampunk

from sensu_go.resources.namespaced import NamespacedResource
from sensu_go.resources.v2 import V2Mixin


class Hook(V2Mixin, NamespacedResource):
    PATH_TEMPLATE = "/api/core/v2/namespaces/{namespace}/hooks"
    TYPE = "HookConfig"
    API_VERSION = "core/v2"
    FIELD_PREFIX = "hook"
