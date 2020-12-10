Sensu Go Python client
======================

This repository contains source code for the official Sensu Go Python client.


Installation
------------

The Sensu Go Python client is available on PyPI and can be installed using
pip. In order to avoid doing any global damage to the system, we can install
it into a dedicated virtual environment like this::

   $ python3 -m venv venv
   $ . venv/bin/activate
   (venv) $ pip install sensu_go


Using the client
----------------

.. note::

   If you would like to follow along in a Python REPL, you can start a
   containerized Sensu Go instance like this::

      $ docker run --rm -p 8080:8080 -p 3000:3000 \
          sensu/sensu sensu-backend start

Before we can start using the client, we need to create one:

.. code-block:: python

   import sensu_go

   client = sensu_go.Client(
       "http://localhost:8080", username="admin", password="P@ssw0rd!"
   )

Now we can list available resources in the `default` namespace:

.. code-block:: python

   print(client.namespaces.list())
   print(client.assets.list())
   print(client.checks.list())

When creating a resource, we need to provide the payload specified in the
Sensu Go's API documentation. For example, this is how we would creae a new
namespace called `demo`:

.. code-block:: python

   ns = client.namespaces.create(dict(name="demo"))
   print(ns)
   print(client.namespaces.list())

Same thing goes for other things like checks and assets:

.. code-block:: python

   asset_data = {
       "metadata": {
           "name": "sensu-slack-handler",
           "namespace": "demo"
       },
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
   }
   client.assets.create(asset_data)

   check_data = {
       "metadata": {
           "name": "check-cpu",
           "namespace": "default"
       },
       "command": "check-cpu.sh -w 75 -c 90",
       "subscriptions": ["linux"],
       "interval": 60,
       "publish": True,
       "handlers": ["slack"],
   }
   check = client.checks.create(check_data)

Once we have a resource object at hand, we can update it and propagate the
changes to the backend::

.. code-block:: python

   # Update local representation
   check["interval"] = 100
   check.update(publish=False, subscriptions=["my-sub"])
   # Propagate the changes
   check.save()

We can also fetch a resource from a non-default namespace (in our case, from
the `demo` namespace):

.. code-block:: python

   asset = client.assets.get("sensu-slack-handler", "demo")
   print(asset)

We can also reload the resource of we expect it to change:

.. code-block:: python

   asset.reload()

And of course, we can also delete the resource:

.. code-block:: python

   # Delete resource via local object
   asset.delete()
   # Or delete it by name (and namespace if applicable)
   client.namespaces.delete("demo")
   # Deleting multiple items is also easy:
   for c in client.checks.list():
       c.delete()

We can also send requests to the backend directly if the resource API is not
available or does not make sense:

.. code-block:: python

   print(client.get("/version"))
   print(client.post("/api/core/v2/namespaces/default/entities", {
       "entity_class": "proxy",
       "subscriptions": ["web"],
       "metadata": {
         "name": "my-entity",
         "namespace": "default",
       }
   }))
   print(client.put("/api/core/v2/namespaces/default/entities/my-entity", {
       "entity_class": "proxy",
       "subscriptions": ["prod"],
       "metadata": {
         "name": "my-entity",
         "namespace": "default",
       }
   }))
   print(client.delete("/api/core/v2/namespaces/default/entities/my-entity"))
