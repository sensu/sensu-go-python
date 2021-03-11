# Copyright (c) 2020 XLAB Steampunk

from typing import List

from sensu_go.resources.base import Resource


class NamespacedResource(Resource):
    def validate(self) -> List[str]:
        result = []
        if "name" not in self.metadata:
            result.append("Namespaced resources need to have a 'name'.")
        if "namespace" not in self.metadata:
            result.append("Namespaced resources need to have a 'namespace'.")
        return result
