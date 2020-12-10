# Copyright (c) 2020 XLAB Steampunk

from typing import List

from sensu_go.resources.base import Resource
from sensu_go.typing import JSONItem


class ClusterResource(Resource):
    @staticmethod
    def validate(data: JSONItem) -> List[str]:
        result = []
        if not data.get("metadata", {}).get("name"):
            result.append("Cluster resources need to have a 'name'.")
        return result
