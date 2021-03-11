# Copyright (c) 2020 XLAB Steampunk

from sensu_go.typing import JSONItem


class V1Mixin:
    @staticmethod
    def api_to_native(data: JSONItem, type: str) -> JSONItem:
        return {k: data[k] for k in ("type", "metadata", "spec")}

    @staticmethod
    def native_to_api(
        spec: JSONItem, metadata: JSONItem, type: str, api_version: str
    ) -> JSONItem:
        return dict(spec=spec, metadata=metadata, type=type, api_version=api_version)
