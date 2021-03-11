# Copyright (c) 2020 XLAB Steampunk

from sensu_go.typing import JSONItem


class V2Mixin:
    @staticmethod
    def api_to_native(data: JSONItem, type: str) -> JSONItem:
        return dict(
            type=type,
            metadata=data["metadata"],
            spec={k: v for k, v in data.items() if k != "namespace"},
        )

    @staticmethod
    def native_to_api(
        spec: JSONItem, metadata: JSONItem, type: str, api_version: str
    ) -> JSONItem:
        return dict(spec, metadata=metadata)
