# Copyright (c) 2020 XLAB Steampunk

import pytest

from sensu_go.clients.http.base import HTTPClient, Response
from sensu_go.errors import ResponseError


class TestResponse:
    def test_valid_json(self, mocker):
        response = mocker.Mock()
        response.url = "https://my.url/"
        response.status_code = 200
        response.text = '{"valid":"json"}'
        response.headers.lower_items.return_value = dict(a="b")

        res = Response(response)

        response.url = "https://my.url/"
        assert res.status == 200
        assert res.text == '{"valid":"json"}'
        assert res.headers == dict(a="b")
        assert res.json == dict(valid="json")
        # We test json twice to also exercise memoization
        assert res.json == dict(valid="json")

    def test_invalid_json(self, mocker):
        response = mocker.Mock()
        response.url = "https://my.url/here"
        response.status_code = 204
        response.text = ""
        response.headers.lower_items.return_value = {}

        res = Response(response)

        assert res.url == "https://my.url/here"
        assert res.status == 204
        assert res.text == ""
        assert res.headers == {}
        with pytest.raises(ResponseError):
            res.json


class DummyClient(HTTPClient):
    @property
    def auth_header_value(self):
        return "dummy header val"


class TestHTTPClientConstructor:
    def test_default(self, mocker):
        session_mock = mocker.patch("requests.Session")

        client = DummyClient("https://my.url")

        assert client.address == "https://my.url"
        session_mock.return_value.verify is True

    def test_trailing_slash_removal(self, mocker):
        session_mock = mocker.patch("requests.Session")

        client = DummyClient("https://my.url/")

        assert client.address == "https://my.url"

    def test_kill_verification(self, mocker):
        session_mock = mocker.patch("requests.Session")

        client = DummyClient("https://my.url", verify=False)

        session_mock.return_value.verify is False

    def test_use_custom_ca_bundle_for_verification(self, mocker):
        session_mock = mocker.patch("requests.Session")

        client = DummyClient("https://my.url", ca_path="some_path")

        session_mock.return_value.verify == "some_path"

    @pytest.mark.parametrize(
        "verify,ca_path,verify_result",
        [
            (True, None, True),
            (False, None, False),
            (True, "ca_bundle", "ca_bundle"),
            (False, "ca_bundle", "ca_bundle"),
        ],
    )
    def test_optional_parameter_combinations(
        self, mocker, verify, ca_path, verify_result
    ):
        session_mock = mocker.patch("requests.Session")

        client = DummyClient("https://my.url", verify=verify, ca_path=ca_path)

        session_mock.return_value.verify == verify_result


class TestHTTPClientRequest:
    def test_auth_header(self, requests_mock):
        # Header value comes from our dummy client class
        requests_mock.get(
            "https://my.url/some/path",
            request_headers=dict(Authorization="dummy header val"),
            status_code=404,
            text="return value",
        )
        client = DummyClient("https://my.url")

        response = client.request("GET", "/some/path")

        assert response.url == "https://my.url/some/path"
        assert response.status == 404
        assert response.text == "return value"


class TestHTTPClientGet:
    def test_right_method(self, requests_mock):
        requests_mock.get("https://my.url/get/path")
        client = DummyClient("https://my.url")

        client.get("/get/path")


class TestHTTPClientGet:
    def test_right_method(self, requests_mock):
        requests_mock.post("https://my.url/post/path")
        client = DummyClient("https://my.url")

        client.post("/post/path", dict(post="data"))


class TestHTTPClientGet:
    def test_right_method(self, requests_mock):
        requests_mock.put("https://my.url/put/path")
        client = DummyClient("https://my.url")

        client.put("/put/path", dict(put="data"))


class TestHTTPClientGet:
    def test_right_method(self, requests_mock):
        requests_mock.delete("https://my.url/delete/path")
        client = DummyClient("https://my.url")

        client.delete("/delete/path")
