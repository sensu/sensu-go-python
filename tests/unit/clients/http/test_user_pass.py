# Copyright (c) 2020 XLAB Steampunk

import pytest

from sensu_go.clients.http.user_pass import UserPassClient
from sensu_go.errors import ResponseError, AuthError


class TestAuthHeaderValue:
    def test_valid_login(self, requests_mock):
        requests_mock.get(
            "https://my.url/auth",
            status_code=200,
            text='{"access_token":"at","refresh_token":"rt"}',
        )
        client = UserPassClient("https://my.url", "user", "pass")

        assert "Bearer at" == client.auth_header_value

    def test_invalid_login(self, requests_mock):
        requests_mock.get(
            "https://my.url/auth",
            status_code=401,
            text='{"access_token":"at","refresh_token":"rt"}',
        )
        client = UserPassClient("https://my.url", "user", "pass")

        with pytest.raises(AuthError, match="credentials"):
            client.auth_header_value

    def test_invalid_json_in_response(self, requests_mock):
        requests_mock.get(
            "https://my.url/auth",
            status_code=200,
            text="} <- not a JSON",
        )
        client = UserPassClient("https://my.url", "user", "pass")

        with pytest.raises(ResponseError, match="decode"):
            client.auth_header_value

    @pytest.mark.parametrize(
        "text",
        [
            "{}",  # Both tokens missing
            '{"access_tken":"at"}',  # Missing refresh token
            '{"refresh_token":"rt"}',  # Missing access token
        ],
    )
    def test_invalid_response_format(self, requests_mock, text):
        requests_mock.get(
            "https://my.url/auth",
            status_code=200,
            text=text,
        )
        client = UserPassClient("https://my.url", "user", "pass")

        with pytest.raises(AuthError, match="tokens"):
            client.auth_header_value

    def test_token_reuse(self, requests_mock):
        mock = requests_mock.get(
            "https://my.url/auth",
            status_code=200,
            text='{"access_token":"at","refresh_token":"rt"}',
        )
        client = UserPassClient("https://my.url", "user", "pass")

        client.auth_header_value
        client.auth_header_value

        assert mock.called_once
