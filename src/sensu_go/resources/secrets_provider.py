# Copyright (c) 2020 XLAB Steampunk

from sensu_go.resources.cluster import ClusterResource
from sensu_go.resources.v1 import V1Mixin


class SecretsProvider(V1Mixin, ClusterResource):
    PATH_TEMPLATE = "/api/enterprise/secrets/v1/providers"
    TYPE = ""  # We set the type to an empty string because user needs to specify it
    API_VERSION = "secrets/v1"
    FIELD_PREFIX = "provider"
