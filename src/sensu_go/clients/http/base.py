# Copyright (c) 2020 XLAB Steampunk

import abc
import json
from typing import cast, Dict, Optional, Tuple

import requests

from sensu_go.errors import HTTPError, ResponseError
from sensu_go.typing import JSON


class Response:
    def __init__(self, response: requests.Response) -> None:
        self.url = response.url
        self.status = response.status_code
        self.text = response.text
        self.headers = dict(response.headers.lower_items())

        self._json: JSON

    @property
    def json(self) -> JSON:
        if not hasattr(self, "_json"):
            try:
                self._json = cast(JSON, json.loads(self.text))
            except json.decoder.JSONDecodeError:
                raise ResponseError(
                    "Cannot decode response", self.url, self.status, self.text
                )
        return self._json

    def __str__(self) -> str:
        return "[{}] {} ({})".format(self.status, self.text, self.headers)


class HTTPClient(abc.ABC):
    def __init__(
        self, address: str, verify: bool = True, ca_path: Optional[str] = None
    ) -> None:
        self.address = address.rstrip("/")

        self.session = requests.Session()
        # Requests use single parameter for verification. We split it into two
        # parameters because this makes interface a bit more readable.
        self.session.verify = ca_path or verify

    @property
    @abc.abstractmethod
    def auth_header_value(self) -> str:
        pass

    def _request(
        self,
        method: str,
        path: str,
        payload: JSON = None,
        headers: Optional[Dict[str, str]] = None,
        query: Optional[Dict[str, str]] = None,
        auth: Optional[Tuple[str, str]] = None,
    ) -> Response:
        headers = headers or {}
        url = self.address + path
        try:
            return Response(
                self.session.request(
                    method, url, json=payload, headers=headers, params=query, auth=auth
                )
            )
        except requests.exceptions.ConnectionError:
            raise HTTPError("{} {} failed".format(method, url))

    def request(
        self,
        method: str,
        path: str,
        payload: JSON = None,
        query: Optional[Dict[str, str]] = None,
    ) -> Response:
        headers = dict(Authorization=self.auth_header_value)
        return self._request(method, path, payload, headers, query)

    def get(
        self,
        path: str,
        query: Optional[Dict[str, str]] = None,
    ) -> Response:
        return self.request("GET", path, query=query)

    def post(self, path: str, payload: JSON) -> Response:
        return self.request("POST", path, payload)

    def put(self, path: str, payload: JSON) -> Response:
        return self.request("PUT", path, payload)

    def delete(self, path: str) -> Response:
        return self.request("DELETE", path)
