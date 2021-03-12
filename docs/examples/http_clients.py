#!/usr/bin/env python3

import sensu_go


def main():
    client = sensu_go.Client(
        "http://localhost:8080", username="admin", password="P@ssw0rd!"
    )

    print(client.get("/version"))
    print(
        client.post(
            "/api/core/v2/namespaces/default/entities",
            {
                "entity_class": "proxy",
                "subscriptions": ["web"],
                "metadata": {
                    "name": "my-entity",
                    "namespace": "default",
                },
            },
        )
    )
    print(
        client.put(
            "/api/core/v2/namespaces/default/entities/my-entity",
            {
                "entity_class": "proxy",
                "subscriptions": ["prod"],
                "metadata": {
                    "name": "my-entity",
                    "namespace": "default",
                },
            },
        )
    )
    print(client.delete("/api/core/v2/namespaces/default/entities/my-entity"))


if __name__ == "__main__":
    main()
