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
   (venv) $ pip install sensu-go


Using the client
----------------

.. note::
   If you would like to follow along in a Python REPL, you can start a
   containerized Sensu Go instance like this::

      $ docker run --rm -p 8080:8080 -p 3000:3000 \
          sensu/sensu sensu-backend start

.. note::
   Version 0.3.0 broke the API compatibility with the previous versions. The
   reason for this API break is generalization and unification of Sensu Go
   management. With new changes in place, managing configuration through the
   resource interface folows the same patterns for both v1 and v2 API endponts.

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
Sensu Go's API documentation. For example, this is how we would create a new
namespace called `demo`:

.. code-block:: python

   ns = client.namespaces.create(metdata={}, spec=dict(name="demo"))
   print(ns)
   print(client.namespaces.list())

Same thing goes for other things like checks and assets:

.. code-block:: python

   client.assets.create(
       metadata={
           "name": "sensu-slack-handler",
           "namespace": "demo"
       },
       spec={
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
   )

   check = client.checks.create(
       metadata={
           "name": "check-cpu",
           "namespace": "default"
       },
       spec={
           "command": "check-cpu.sh -w 75 -c 90",
           "subscriptions": ["linux"],
           "interval": 60,
           "publish": True,
           "handlers": ["slack"],
       },
   )

Once we have a resource object at hand, we can update it and propagate the
changes to the backend:

.. code-block:: python

   # Update local representation
   check.spec["interval"] = 100
   check.spec.update(publish=False, subscriptions=["my-sub"])
   # Propagate the changes
   check.save()

We can also fetch a resource from a non-default namespace (in our case, from
the `demo` namespace):

.. code-block:: python

   asset = client.assets.get("sensu-slack-handler", "demo")
   print(asset)

We can also reload the resource if we expect it to change:

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

The ``get`` method will fail spectacularly if the resource we are trying to
fetch does not exist on the backend. If we would like to check the presence of
a resource, we can use the ``find`` method:

.. code-block:: python

   hook = client.hooks.find("hook-that-might-not-exist")
   if hook:
       print("We do have a hook!")
   else:
       print("No hook on the backend.")

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
