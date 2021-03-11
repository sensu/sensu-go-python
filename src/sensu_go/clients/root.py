# Copyright (c) 2020 XLAB Steampunk

from typing import Optional

from sensu_go.clients.http.base import HTTPClient, Response
from sensu_go.clients.http.user_pass import UserPassClient

from sensu_go.clients.resource.cluster import ClusterClient
from sensu_go.clients.resource.namespaced import NamespacedClient

from sensu_go.resources.asset import Asset
from sensu_go.resources.check import Check
from sensu_go.resources.entity import Entity
from sensu_go.resources.event import Event
from sensu_go.resources.filter import Filter
from sensu_go.resources.handler import Handler
from sensu_go.resources.hook import Hook
from sensu_go.resources.mutator import Mutator
from sensu_go.resources.secret import Secret
from sensu_go.resources.secrets_provider import SecretsProvider
from sensu_go.resources.silence import Silence

from sensu_go.resources.namespace import Namespace

from sensu_go.typing import JSON


def _get_http_client(
    address: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    verify: bool = True,
    ca_path: Optional[str] = None,
) -> HTTPClient:
    # TODO(@tadeboro): Add parameter validation
    if username and password:
        return UserPassClient(address, username, password, verify, ca_path)
    raise ValueError("Invalid set of client arguments.")


class Client:
    def __init__(
        self,
        address: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        default_namespace: str = "default",
        verify: bool = True,
        ca_path: Optional[str] = None,
    ) -> None:
        self._client = _get_http_client(address, username, password, verify, ca_path)

        # Namespaced API
        ns = default_namespace
        self.assets = NamespacedClient(self._client, Asset, ns)
        self.checks = NamespacedClient(self._client, Check, ns)
        self.entities = NamespacedClient(self._client, Entity, ns)
        self.events = NamespacedClient(self._client, Event, ns)
        self.filters = NamespacedClient(self._client, Filter, ns)
        self.handlers = NamespacedClient(self._client, Handler, ns)
        self.hooks = NamespacedClient(self._client, Hook, ns)
        self.mutators = NamespacedClient(self._client, Mutator, ns)
        self.secrets = NamespacedClient(self._client, Secret, ns)
        self.silences = NamespacedClient(self._client, Silence, ns)

        # Cluster-wide API
        self.namespaces = ClusterClient(self._client, Namespace)
        self.secrets_providers = ClusterClient(self._client, SecretsProvider)

    def get(self, path: str) -> Response:
        return self._client.get(path)

    def post(self, path: str, payload: JSON) -> Response:
        return self._client.post(path, payload)

    def put(self, path: str, payload: JSON) -> Response:
        return self._client.put(path, payload)

    def delete(self, path: str) -> Response:
        return self._client.delete(path)
