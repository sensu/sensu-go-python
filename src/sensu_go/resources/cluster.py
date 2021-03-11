# Copyright (c) 2020 XLAB Steampunk

from typing import List

from sensu_go.resources.base import Resource


class ClusterResource(Resource):
    def validate(self) -> List[str]:
        result = []
        if "name" not in self.metadata:
            result.append("Cluster resources need to have a 'name'.")
        return result
