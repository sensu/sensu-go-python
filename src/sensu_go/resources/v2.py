# Copyright (c) 2020 XLAB Steampunk

from sensu_go.typing import JSONItem


class V2Mixin:
    @staticmethod
    def api_to_native(data: JSONItem) -> JSONItem:
        return data

    @staticmethod
    def native_to_api(data: JSONItem) -> JSONItem:
        return data
