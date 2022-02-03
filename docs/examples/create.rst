Example - create data
=====================

Open a python shell in interactive mode (run `python3`) and run the following commands in sequence.


First we'll import the library and make a new store.

.. code-block:: python

    from ocdsmetricsanalysis.library import Store
    store = Store("example-create.sqlite")

Currently the store is empty, as you can see by getting a list of current metrics.

.. code-block:: python

   print(store.get_metrics())

We'll add our own metric!

.. code-block:: python

   store.add_metric("HATS", "How many people like hats?", "We ran a survey to find out.")
   metric = store.get_metric("HATS")


Now we have our metric, but we need to add some observations to it.

.. code-block:: python

   metric.add_observation("obs1", measure=34, dimensions={'answer':'like'})
   metric.add_observation("obs2", measure=15, dimensions={'answer':'neither like or dislike'})
   metric.add_observation("obs3", measure=12, dimensions={'answer':'dislike'})

Now our store contains some data - we can export this as JSON.

.. code-block:: python

    import json
    json_data = metric.get_json()
    print(json.dumps(json_data, indent=4))

You should see something like:


.. code-block:: json

   {
        "id": "HATS",
        "title": "How many people like hats?",
        "description": "We ran a survey to find out.",
        "observations": [
            {
                "id": "obs1",
                "dimensions": {
                    "answer": "like"
                },
                "measure": "34"
            },
            {
                "id": "obs2",
                "dimensions": {
                    "answer": "neither like or dislike"
                },
                "measure": "15"
            },
            {
                "id": "obs3",
                "dimensions": {
                    "answer": "dislike"
                },
                "measure": "12"
            }
        ]
   }

You can save this to disk as normal


.. code-block:: python


   with open("output.json", "w") as fp:
       json.dump(json_data, fp, indent=4)
