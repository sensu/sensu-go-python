# Copyright (c) 2021 XLAB Steampunk

from sensu_go.resources.namespaced import NamespacedResource
from sensu_go.resources.v1 import V1Mixin


class Secret(V1Mixin, NamespacedResource):
    PATH_TEMPLATE = "/api/enterprise/secrets/v1/namespaces/{namespace}/secrets"
    TYPE = "Secret"
    API_VERSION = "secrets/v1"
    FIELD_PREFIX = "secret"
