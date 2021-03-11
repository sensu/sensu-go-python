# Copyright (c) 2021 XLAB Steampunk

from sensu_go.resources.namespaced import NamespacedResource
from sensu_go.resources.v2 import V2Mixin


class Mutator(V2Mixin, NamespacedResource):
    PATH_TEMPLATE = "/api/core/v2/namespaces/{namespace}/mutators"
    TYPE = "Mutator"
    API_VERSION = "core/v2"
