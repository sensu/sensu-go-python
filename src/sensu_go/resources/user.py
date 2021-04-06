# Copyright (c) 2020 XLAB Steampunk

from typing import cast, List

from sensu_go.resources.cluster import ClusterResource
from sensu_go.typing import JSONItem


class User(ClusterResource):
    PATH_TEMPLATE = "/api/core/v2/users"
    TYPE = "User"
    API_VERSION = "core/v2"
    FIELD_PREFIX = "user"

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

        if not self.spec.get("username"):
            result.append("Users needs to have a 'username'.")

        if not self.spec.get("password") and not self.spec.get("password_hash"):
            result.append("Users needs to have a 'password' or 'password_hash'.")

        return result

    def delete(self) -> None:
        raise Exception("Users cannot be deleted")

    @property
    def name(self) -> str:
        return cast(str, self.spec["username"])
