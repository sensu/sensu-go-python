# Copyright (c) 2020 XLAB Steampunk

from typing import Any, Dict, List, Union


# Custom JSON type. Does not validate much, but at least we have a sensible
# type annotation. For more powerful checking, mypy needs to understand
# recursive types.
JSONItem = Dict[str, Any]
JSONList = List[Any]
JSON = Union[bool, float, int, str, JSONList, JSONItem, None]
