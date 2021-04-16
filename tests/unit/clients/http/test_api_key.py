# Copyright (c) 2021 XLAB Steampunk

from sensu_go.clients.http.api_key import ApiKeyClient


class TestAuthHeaderValue:
    def test_retrieval(self):
        client = ApiKeyClient("https://my.url", "api_key")

        assert "Key api_key" == client.auth_header_value
