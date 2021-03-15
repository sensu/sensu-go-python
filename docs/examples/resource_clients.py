#!/usr/bin/env python3

import functools

import sensu_go
from sensu_go import errors


def main():
    # Initialize client
    client = sensu_go.Client(
        "http://localhost:8080", username="admin", password="P@ssw0rd!"
    )

    # Cluster resources
    demo_namespaces(client)
    demo_secrets_providers(client)

    # Namespaced resources
    demo_ns = client.namespaces.create(metadata={}, spec={"name": "demo"})

    demo_assets(client)
    demo_checks(client)
    demo_entities(client)
    demo_filters(client)
    demo_handlers(client)
    demo_hooks(client)
    demo_mutators(client)
    demo_secrets(client)
    demo_silences(client)

    # Events are a bit special
    demo_events(client)


def delimit(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("\n{} =====================".format(func.__name__))
        func(*args, **kwargs)
        print("================================\n")

    return wrapper


def print_namespaced_resource(resource):
    print("Namespaced resource")
    print("  Name: " + resource.name)
    print("  Namespace: " + resource.namespace)
    print("  API path: " + resource.path)
    print("  Spec: " + str(resource.spec))
    print("  Metadata: " + str(resource.metadata))
    print("  API version: " + resource.api_version)
    print("  Type: " + resource.type)


def print_cluster_resource(resource):
    print("Cluster resource")
    print("  Name: " + resource.name)
    print("  API path: " + resource.path)
    print("  Spec: " + str(resource.spec))
    print("  Metadata: " + str(resource.metadata))
    print("  API version: " + resource.api_version)
    print("  Type: " + resource.type)


def printiter(iter):
    print("[{}]".format(", ".join(str(i) for i in iter)))


@delimit
def demo_namespaces(client):
    # Find does not fail if resource does not exist, it returns None
    print(client.namespaces.find("nonexistent"))

    # Get fails if it canot retrieve a resource
    try:
        client.namespaces.get("nonexistent")
    except errors.SensuError as e:
        print(e)

    # Create
    namespace = client.namespaces.create(metadata={}, spec={"name": "demo"})
    print_cluster_resource(namespace)
    client.namespaces.create(metadata={}, spec={"name": "dummy"})

    # List
    printiter(client.namespaces.list())

    # Delete
    namespace.delete()
    client.namespaces.delete("dummy")
    printiter(client.namespaces.list())


@delimit
def demo_secrets_providers(client):
    # Find does not fail if resource does not exist, it returns None
    print(client.secrets_providers.find("nonexistent"))

    # Get fails if it canot retrieve a resource
    try:
        client.secrets_providers.get("nonexistent")
    except errors.SensuError as e:
        print(e)

    # Create
    provider = client.secrets_providers.create(
        type="VaultProvider",
        metadata={"name": "my_vault"},
        spec={
            "client": {
                "address": "http://vaultserver.example.com:8200",
                "token": "VAULT_TOKEN",
                "version": "v1",
                "max_retries": 2,
                "timeout": "20s",
                "rate_limiter": {"limit": 10.0, "burst": 100},
            }
        },
    )
    print_cluster_resource(provider)

    # List
    printiter(client.secrets_providers.list())

    # Update
    provider.spec["max_retries"] = 3
    provider.save()
    print_cluster_resource(provider)

    # If we are expecting the resource on the backend to change, we can reload the data
    provider.reload()

    # Delete
    provider.delete()
    # client.secrets_providers.delete("my_vault")  # Can also delete by name


@delimit
def demo_assets(client):
    # Find does not fail if resource does not exist, it returns None
    print(client.assets.find("nonexistent"))
    print(client.assets.find("nonexistent", "bad-namespace"))

    # Get fails if it canot retrieve a resource
    try:
        client.assets.get("nonexistent")
    except errors.SensuError as e:
        print(e)
    try:
        client.assets.get("nonexistent", "bad-namespace")
    except errors.SensuError as e:
        print(e)

    # Create
    try:
        client.assets.create(metadata={"name": "my_asset"}, spec={"bad": "data"})
    except errors.SensuError as e:
        print(e)

    asset = client.assets.create(
        metadata={
            "name": "sensu-slack-handler",
            # No namespace -> goes into the default namespace that we declared at
            # client creation time.
        },
        spec={
            "builds": [
                {
                    "url": "https://github.com/sensu/sensu-slack-handler/releases/download/1.0.3/sensu-slack-handler_1.0.3_linux_amd64.tar.gz",
                    "sha512": "68720865127fbc7c2fe16ca4d7bbf2a187a2df703f4b4acae1c93e8a66556e9079e1270521999b5871473e6c851f51b34097c54fdb8d18eedb7064df9019adc8",
                    "filters": [
                        "entity.system.os == 'linux'",
                        "entity.system.arch == 'amd64'",
                    ],
                    "headers": {
                        "Authorization": "Bearer $TOKEN",
                        "X-Forwarded-For": "client1, proxy1, proxy2",
                    },
                },
            ],
        },
    )
    print_namespaced_resource(asset)
    client.assets.create(
        metadata={
            "name": "sensu-slack-handler",
            "namespace": "demo",
        },
        spec={
            "builds": [
                {
                    "url": "https://github.com/sensu/sensu-slack-handler/releases/download/1.0.3/sensu-slack-handler_1.0.3_linux_amd64.tar.gz",
                    "sha512": "68720865127fbc7c2fe16ca4d7bbf2a187a2df703f4b4acae1c93e8a66556e9079e1270521999b5871473e6c851f51b34097c54fdb8d18eedb7064df9019adc8",
                },
            ],
        },
    )

    # List
    printiter(client.assets.list())
    printiter(client.assets.list("demo"))

    # Update
    asset.spec["builds"][0]["url"] = "https://my.new.url/asset.tar.gz"
    asset.save()
    print_namespaced_resource(asset)

    # If we are expecting the resource on the backend to change, we can reload the data
    asset.reload()

    # Delete
    asset.delete()
    printiter(client.assets.list())
    printiter(client.assets.list("demo"))
    client.assets.delete("sensu-slack-handler", "demo")
    printiter(client.assets.list())
    printiter(client.assets.list("demo"))


@delimit
def demo_checks(client):
    # Find does not fail if resource does not exist, it returns None
    print(client.checks.find("nonexistent"))
    print(client.checks.find("nonexistent", "bad-namespace"))

    # Get fails if it canot retrieve a resource
    try:
        client.checks.get("nonexistent")
    except errors.SensuError as e:
        print(e)
    try:
        client.checks.get("nonexistent", "bad-namespace")
    except errors.SensuError as e:
        print(e)

    # Create
    try:
        client.checks.create(metadata={"name": "my_check"}, spec={"bad": "data"})
    except errors.SensuError as e:
        print(e)

    check = client.checks.create(
        metadata={"name": "check_minimum"},
        spec={
            "command": "collect.sh",
            "subscriptions": ["system"],
            "handlers": ["slack"],
            "interval": 10,
            "publish": True,
        },
    )
    print_namespaced_resource(check)
    client.checks.create(
        metadata={
            "name": "check_minimum",
            "namespace": "demo",
        },
        spec={
            "command": "collect.sh",
            "subscriptions": ["system"],
            "handlers": ["slack"],
            "interval": 10,
            "publish": True,
        },
    )

    # List
    printiter(client.checks.list())
    printiter(client.checks.list("demo"))

    # Update
    check.spec["command"] = "fancy_collect.sh"
    check.save()
    print_namespaced_resource(check)

    # If we are expecting the resource on the backend to change, we can reload the data
    check.reload()

    # Delete
    check.delete()
    printiter(client.checks.list())
    printiter(client.checks.list("demo"))
    client.checks.delete("check_minimum", "demo")
    printiter(client.checks.list())
    printiter(client.checks.list("demo"))


@delimit
def demo_entities(client):
    # Find does not fail if resource does not exist, it returns None
    print(client.entities.find("nonexistent"))
    print(client.entities.find("nonexistent", "bad-namespace"))

    # Get fails if it canot retrieve a resource
    try:
        client.entities.get("nonexistent")
    except errors.SensuError as e:
        print(e)
    try:
        client.entities.get("nonexistent", "bad-namespace")
    except errors.SensuError as e:
        print(e)

    # Create
    try:
        client.entities.create(metadata={"name": "my_entity"}, spec={"bad": "data"})
    except errors.SensuError as e:
        print(e)

    entity = client.entities.create(
        metadata={
            "name": "sensu-docs",
        },
        spec={
            "deregister": False,
            "deregistration": {},
            "entity_class": "proxy",
            "last_seen": 0,
            "subscriptions": ["proxy"],
            "sensu_agent_version": "1.0.0",
        },
    )
    print_namespaced_resource(entity)
    client.entities.create(
        metadata={
            "name": "sensu-docs",
            "namespace": "demo",
        },
        spec={
            "deregister": False,
            "deregistration": {},
            "entity_class": "proxy",
            "last_seen": 0,
            "subscriptions": ["proxy"],
            "sensu_agent_version": "1.0.0",
        },
    )

    # List
    printiter(client.entities.list())

    # Update
    entity.spec["deregister"] = True
    entity.save()
    print_namespaced_resource(entity)

    # If we are expecting the resource on the backend to change, we can reload the data
    entity.reload()

    # Delete
    entity.delete()
    client.entities.delete("sensu-docs", "demo")
    printiter(client.entities.list())


@delimit
def demo_events(client):
    printiter(client.events.list())
    printiter(client.events.list("demo"))

    client.events.create(
        metadata={},
        spec={
            "entity": {"entity_class": "proxy", "metadata": {"name": "server1"}},
            "check": {
                "output": "Server error",
                "silenced": ["entity:gin:server-health"],
                "state": "failing",
                "status": 2,
                "handlers": ["slack"],
                "interval": 60,
                "is_silenced": True,
                "metadata": {"name": "server-health"},
            },
        },
    )

    printiter(client.events.list())
    printiter(client.events.list("demo"))

    c = client.checks.create(
        metadata={
            "name": "server-health",
            "namespace": "demo",
        },
        spec={
            "command": "collect.sh",
            "subscriptions": ["system"],
            "handlers": ["slack"],
            "interval": 10,
            "publish": True,
        },
    )
    event = client.events.create(
        metadata={"namespace": "demo"},
        spec={
            "entity": {"entity_class": "proxy", "metadata": {"name": "server1"}},
            "check": {
                "output": "Server error",
                "silenced": ["entity:gin:server-health"],
                "state": "failing",
                "status": 2,
                "handlers": ["slack"],
                "interval": 60,
                "is_silenced": True,
                "metadata": {"name": "server-health"},
            },
        },
    )

    printiter(client.events.list())
    printiter(client.events.list("demo"))

    printiter(client.checks.list("demo"))
    printiter(c.events)

    c.events.delete()

    printiter(client.events.list())
    printiter(client.events.list("demo"))

    client.events.delete("server1/server-health")

    printiter(client.events.list())
    printiter(client.events.list("demo"))


@delimit
def demo_filters(client):
    # Find does not fail if resource does not exist, it returns None
    print(client.filters.find("nonexistent"))
    print(client.filters.find("nonexistent", "bad-namespace"))

    # Get fails if it canot retrieve a resource
    try:
        client.filters.get("nonexistent")
    except errors.SensuError as e:
        print(e)
    try:
        client.filters.get("nonexistent", "bad-namespace")
    except errors.SensuError as e:
        print(e)

    # Create
    try:
        client.filters.create(metadata={"name": "my_filter"}, spec={"bad": "data"})
    except errors.SensuError as e:
        print(e)

    filter = client.filters.create(
        metadata={
            "name": "filter_minimum",
        },
        spec={"action": "allow", "expressions": ["event.check.occurrences == 1"]},
    )
    print_namespaced_resource(filter)
    client.filters.create(
        metadata={
            "name": "filter_minimum",
            "namespace": "demo",
        },
        spec={"action": "allow", "expressions": ["event.check.occurrences == 1"]},
    )

    # List
    printiter(client.filters.list())

    # Update
    filter.spec["action"] = "deny"
    filter.save()
    print_namespaced_resource(filter)

    # If we are expecting the resource on the backend to change, we can reload the data
    filter.reload()

    # Delete
    filter.delete()
    client.filters.delete("filter_minimum", "demo")
    printiter(client.filters.list())


@delimit
def demo_handlers(client):
    # Find does not fail if resource does not exist, it returns None
    print(client.handlers.find("nonexistent"))
    print(client.handlers.find("nonexistent", "bad-namespace"))

    # Get fails if it canot retrieve a resource
    try:
        client.handlers.get("nonexistent")
    except errors.SensuError as e:
        print(e)
    try:
        client.handlers.get("nonexistent", "bad-namespace")
    except errors.SensuError as e:
        print(e)

    # Create
    try:
        client.handlers.create(metadata={"name": "my_handler"}, spec={"bad": "data"})
    except errors.SensuError as e:
        print(e)

    handler = client.handlers.create(
        metadata={
            "name": "pipe_handler_minimum",
        },
        spec={"command": "command-example", "type": "pipe"},
    )
    print_namespaced_resource(handler)
    client.handlers.create(
        metadata={
            "name": "pipe_handler_minimum",
            "namespace": "demo",
        },
        spec={"command": "command-example", "type": "pipe"},
    )

    # List
    printiter(client.handlers.list())

    # Update
    handler.spec["command"] = "other-command"
    handler.save()
    print_namespaced_resource(handler)

    # If we are expecting the resource on the backend to change, we can reload the data
    handler.reload()

    # Delete
    handler.delete()
    client.handlers.delete("pipe_handler_minimum", "demo")
    printiter(client.handlers.list())


@delimit
def demo_hooks(client):
    # Find does not fail if resource does not exist, it returns None
    print(client.hooks.find("nonexistent"))
    print(client.hooks.find("nonexistent", "bad-namespace"))

    # Get fails if it canot retrieve a resource
    try:
        client.hooks.get("nonexistent")
    except errors.SensuError as e:
        print(e)
    try:
        client.hooks.get("nonexistent", "bad-namespace")
    except errors.SensuError as e:
        print(e)

    # Create
    try:
        client.hooks.create(metadata={"name": "my_hook"}, spec={"bad": "data"})
    except errors.SensuError as e:
        print(e)

    hook = client.hooks.create(
        metadata={
            "name": "process_tree",
        },
        spec={
            "command": "ps aux",
            "timeout": 60,
            "stdin": False,
        },
    )
    print_namespaced_resource(hook)
    client.hooks.create(
        metadata={
            "name": "process_tree",
            "namespace": "demo",
        },
        spec={
            "command": "ps aux",
            "timeout": 60,
            "stdin": False,
        },
    )

    # List
    printiter(client.hooks.list())

    # Update
    hook.spec["timeout"] = 30
    hook.save()
    print_namespaced_resource(hook)

    # If we are expecting the resource on the backend to change, we can reload the data
    hook.reload()

    # Delete
    hook.delete()
    client.hooks.delete("process_tree", "demo")
    printiter(client.hooks.list())


@delimit
def demo_mutators(client):
    # Find does not fail if resource does not exist, it returns None
    print(client.mutators.find("nonexistent"))
    print(client.mutators.find("nonexistent", "bad-namespace"))

    # Get fails if it canot retrieve a resource
    try:
        client.mutators.get("nonexistent")
    except errors.SensuError as e:
        print(e)
    try:
        client.mutators.get("nonexistent", "bad-namespace")
    except errors.SensuError as e:
        print(e)

    # Create
    try:
        client.mutators.create(metadata={"name": "my_mutator"}, spec={"bad": "data"})
    except errors.SensuError as e:
        print(e)

    mutator = client.mutators.create(
        metadata={
            "name": "example-mutator",
        },
        spec={
            "command": "example_mutator.go",
            "timeout": 0,
            "env_vars": ["MY_VAR=my_value"],
        },
    )
    print_namespaced_resource(mutator)
    client.mutators.create(
        metadata={
            "name": "example-mutator",
            "namespace": "demo",
        },
        spec={
            "command": "example_mutator.go",
            "timeout": 0,
            "env_vars": ["MY_VAR=my_value"],
        },
    )

    # List
    printiter(client.mutators.list())

    # Update
    mutator.spec["env_vars"].extend("ANOTHER_VAR=second_value")
    mutator.save()
    print_namespaced_resource(mutator)

    # If we are expecting the resource on the backend to change, we can reload the data
    mutator.reload()

    # Delete
    mutator.delete()
    client.mutators.delete("example-mutator", "demo")
    printiter(client.mutators.list())


@delimit
def demo_secrets(client):
    # Find does not fail if resource does not exist, it returns None
    print(client.secrets.find("nonexistent"))
    print(client.secrets.find("nonexistent", "bad-namespace"))

    # Get fails if it canot retrieve a resource
    try:
        client.secrets.get("nonexistent")
    except errors.SensuError as e:
        print(e)
    try:
        client.secrets.get("nonexistent", "bad-namespace")
    except errors.SensuError as e:
        print(e)

    # Create
    try:
        client.secrets.create(metadata={"name": "secret"}, spec={"bad": "data"})
    except errors.SensuError as e:
        print(e)

    secret = client.secrets.create(
        metadata={
            "name": "sensu-ansible-token",
        },
        spec={"id": "ANSIBLE_TOKEN", "provider": "env"},
    )
    print_namespaced_resource(secret)
    client.secrets.create(
        metadata={"name": "sensu-ansible-token", "namespace": "demo"},
        spec={"id": "ANSIBLE_TOKEN", "provider": "env"},
    )

    # List
    printiter(client.secrets.list())

    # Update
    secret.spec["id"] = "OTHER_TOKEN"
    secret.save()
    print_namespaced_resource(secret)

    # If we are expecting the resource on the backend to change, we can reload the data
    secret.reload()

    # Delete
    secret.delete()
    client.secrets.delete("sensu-ansible-token", "demo")
    printiter(client.secrets.list())


@delimit
def demo_silences(client):
    # Find does not fail if resource does not exist, it returns None
    print(client.silences.find("nonexistent"))
    print(client.silences.find("nonexistent", "bad-namespace"))

    # Get fails if it canot retrieve a resource
    try:
        client.silences.get("nonexistent")
    except errors.SensuError as e:
        print(e)
    try:
        client.silences.get("nonexistent", "bad-namespace")
    except errors.SensuError as e:
        print(e)

    # Create
    try:
        client.silences.create(metadata={"name": "my_silence"}, spec={"bad": "data"})
    except errors.SensuError as e:
        print(e)

    silence = client.silences.create(
        metadata={
            "name": "entity:i-424242:check_ntp",
        },
        spec={
            "subscription": "entity:i-424242",
            "check": "check_ntp",
            "expire_on_resolve": True,
        },
    )
    print_namespaced_resource(silence)
    client.silences.create(
        metadata={
            "name": "entity:i-424242:check_ntp",
            "namespace": "demo",
        },
        spec={
            "subscription": "entity:i-424242",
            "check": "check_ntp",
            "expire_on_resolve": True,
        },
    )

    # List
    printiter(client.silences.list())

    # Update
    silence.spec["expire_on_resolve"] = False
    silence.save()
    print_namespaced_resource(silence)

    # If we are expecting the resource on the backend to change, we can reload the data
    silence.reload()

    # Delete
    silence.delete()
    client.silences.delete("entity:i-424242:check_ntp", "demo")
    printiter(client.silences.list())


if __name__ == "__main__":
    main()
