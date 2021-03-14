# Copyright (c) 2021 XLAB Steampunk

import pytest

from sensu_go.clients.resource import operator


class TestEqual:
    @pytest.mark.parametrize(
        "selector,value,result",
        [
            ("a", "b", 'a == "b"'),
            ("a", 1, "a == 1"),
            ("a", 2.0, "a == 2.0"),
            ("a", True, "a == true"),
            ("a", False, "a == false"),
        ],
    )
    def test_label_serialization(self, selector, value, result):
        assert result == operator.Equal(selector, value).serialize()

    @pytest.mark.parametrize(
        "selector,value,result",
        [
            ("e", "b", 'res.e == "b"'),
            ("e", 1, "res.e == 1"),
            ("e", 2.0, "res.e == 2.0"),
            ("e", True, "res.e == true"),
            ("e", False, "res.e == false"),
        ],
    )
    def test_field_serialization(self, selector, value, result):
        assert result == operator.Equal(selector, value).serialize("res")


class TestNotEqual:
    @pytest.mark.parametrize(
        "selector,value,result",
        [
            ("j", "b", 'j != "b"'),
            ("j", 1, "j != 1"),
            ("j", 2.0, "j != 2.0"),
            ("j", True, "j != true"),
            ("j", False, "j != false"),
        ],
    )
    def test_label_serialization(self, selector, value, result):
        assert result == operator.NotEqual(selector, value).serialize()

    @pytest.mark.parametrize(
        "selector,value,result",
        [
            ("o", "b", 'pf.o != "b"'),
            ("o", 1, "pf.o != 1"),
            ("o", 2.0, "pf.o != 2.0"),
            ("o", True, "pf.o != true"),
            ("o", False, "pf.o != false"),
        ],
    )
    def test_field_serialization(self, selector, value, result):
        assert result == operator.NotEqual(selector, value).serialize("pf")


class TestMatches:
    def test_label_serialization(self):
        assert 'c matches "d-e"' == operator.Matches("c", "d-e").serialize()

    def test_field_serialization(self):
        assert 'pref.c matches "d-e"' == operator.Matches("c", "d-e").serialize("pref")


class TestIn:
    @pytest.mark.parametrize(
        "left,right,result",
        [
            ("a", "b", '"a" in b'),
            ("a", ["1", "2"], 'a in ["1","2"]'),
        ],
    )
    def test_label_serialization(self, left, right, result):
        assert result == operator.In(left, right).serialize()

    @pytest.mark.parametrize(
        "left,right,result",
        [
            ("a", "b", '"a" in pre.b'),
            ("a", ["1", "2"], 'pre.a in ["1","2"]'),
        ],
    )
    def test_field_serialization(self, left, right, result):
        assert result == operator.In(left, right).serialize("pre")


class TestNotIn:
    @pytest.mark.parametrize(
        "left,right,result",
        [
            ("a", "b", '"a" notin b'),
            ("a", ["1", "2"], 'a notin ["1","2"]'),
        ],
    )
    def test_label_serialization(self, left, right, result):
        assert result == operator.NotIn(left, right).serialize()

    @pytest.mark.parametrize(
        "left,right,result",
        [
            ("a", "b", '"a" notin pre.b'),
            ("a", ["1", "2"], 'pre.a notin ["1","2"]'),
        ],
    )
    def test_field_serialization(self, left, right, result):
        assert result == operator.NotIn(left, right).serialize("pre")


class TestAnd:
    def test_label_serialization(self):
        assert operator.And(
            operator.Equal("a", 3),
            operator.NotEqual("b", False),
            operator.Matches("c", "d-"),
            operator.In("e", ("f", "g")),
            operator.NotIn("h", "i"),
        ).serialize() == (
            "a == 3 && "
            "b != false && "
            'c matches "d-" && '
            'e in ["f","g"] && '
            '"h" notin i'
        )

    def test_field_serialization(self):
        assert operator.And(
            operator.Equal("j", 4.0),
            operator.NotEqual("k", True),
            operator.Matches("l", ":m"),
            operator.In("n", ("o", "p")),
            operator.NotIn("q", "r"),
        ).serialize("x") == (
            "x.j == 4.0 && "
            "x.k != true && "
            'x.l matches ":m" && '
            'x.n in ["o","p"] && '
            '"q" notin x.r'
        )
