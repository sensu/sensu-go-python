# Copyright (c) 2021 XLAB Steampunk

from typing import Optional

from sensu_go.clients.http.base import HTTPClient


class ApiKeyClient(HTTPClient):
    def __init__(
        self,
        address: str,
        api_key: str,
        verify: bool = True,
        ca_path: Optional[str] = None,
    ) -> None:
        super().__init__(address, verify, ca_path)

        self._auth_header_value = "Key " + api_key

    @property
    def auth_header_value(self) -> str:
        return self._auth_header_value
