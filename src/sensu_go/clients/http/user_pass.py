# Copyright (c) 2020 XLAB Steampunk

from typing import cast, Optional

from sensu_go import errors
from sensu_go.clients.http.base import HTTPClient
from sensu_go.typing import JSONItem


class UserPassClient(HTTPClient):
    def __init__(
        self,
        address: str,
        username: str,
        password: str,
        verify: bool = True,
        ca_path: Optional[str] = None,
    ) -> None:
        super().__init__(address, verify, ca_path)

        self._username = username
        self._password = password

        self._access_token: str
        self._refresh_token: str
        self._auth_header_value: str

    @property
    def auth_header_value(self) -> str:
        if not hasattr(self, "_auth_header_value"):
            self._login()
            self._auth_header_value = "Bearer " + self._access_token
        return self._auth_header_value

    def _login(self) -> None:
        auth = (self._username, self._password)
        resp = self._request("GET", "/auth", auth=auth)

        if resp.status != 200:
            raise errors.AuthError(
                "Authentication failed. Verify your credentials.",
                resp.url,
                resp.status,
                resp.text,
            )

        try:
            tokens = cast(JSONItem, resp.json)
            self._access_token, self._refresh_token = (
                cast(str, tokens["access_token"]),
                cast(str, tokens["refresh_token"]),
            )
        except KeyError:
            raise errors.AuthError(
                "Authentication call did not return required tokens",
                resp.url,
                resp.status,
                resp.text,
            )
