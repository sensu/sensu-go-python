# Copyright (c) 2021 XLAB Steampunk

import abc
from typing import Iterable, Optional, Union


def _add_prefix(selector: str, prefix: Optional[str]) -> str:
    return "{}.{}".format(prefix, selector) if prefix else selector


class Operator(metaclass=abc.ABCMeta):
    OPERATOR: str

    @abc.abstractmethod
    def serialize(self, resource: Optional[str] = None) -> str:
        pass


class EqNotEqOperator(Operator):
    def __init__(self, selector: str, value: Union[str, int, float, bool]) -> None:
        self._selector = selector
        self._value = value

    def serialize(self, resource: Optional[str] = None) -> str:
        selector = _add_prefix(self._selector, resource)
        if isinstance(self._value, str):
            # Wrap strings in double quotes because we have no control over the contents
            # and the Sensu Go backend expects certain strings to be quoted.
            value = '"{}"'.format(self._value)
        elif isinstance(self._value, bool):
            value = str(self._value).lower()
        else:
            value = str(self._value)

        return "{} {} {}".format(selector, self.OPERATOR, value)


class Equal(EqNotEqOperator):
    OPERATOR = "=="


class NotEqual(EqNotEqOperator):
    OPERATOR = "!="


class Matches(Operator):
    OPERATOR = "matches"

    def __init__(self, selector: str, value: str) -> None:
        self._selector = selector
        self._value = value

    def serialize(self, resource: Optional[str] = None) -> str:
        selector = _add_prefix(self._selector, resource)
        return '{} {} "{}"'.format(selector, self.OPERATOR, self._value)


class SetOperator(Operator):
    def __init__(self, left: str, right: Union[Iterable[str], str]) -> None:
        self._left = left
        self._right = right

    def serialize(self, resource: Optional[str] = None) -> str:
        if isinstance(self._right, str):
            left = '"{}"'.format(self._left)
            right = _add_prefix(self._right, resource)
        else:
            left = _add_prefix(self._left, resource)
            right = "[{}]".format(",".join('"{}"'.format(v) for v in self._right))

        return "{} {} {}".format(left, self.OPERATOR, right)


class In(SetOperator):
    OPERATOR = "in"


class NotIn(SetOperator):
    OPERATOR = "notin"


class And(Operator):
    OPERATOR = "&&"

    def __init__(self, *args: Operator) -> None:
        self._args = args

    def serialize(self, resource: Optional[str] = None) -> str:
        return (" " + self.OPERATOR + " ").join(
            op.serialize(resource) for op in self._args
        )
