How to import data
==================


Start by getting a data file:

.. code-block:: bash

   wget -O sample_data.json https://raw.githubusercontent.com/OpenDataServices/ocds-metrics-analysis/main/tests/data/one_dimension.json

Now open a python shell in interactive mode (run `python3`) and run the following commands in sequence.


First we'll import the library and make a new store.

.. code-block:: python

    from ocdsmetricsanalysis.library import Store
    store = Store("how-to-import.sqlite")

Currently the store is empty, as you can see by getting a list of current metrics.

.. code-block:: python

   print(store.get_metrics())

We'll load in the data we got in our sample JSON file.


.. code-block:: python

    import json
    with open("sample_data.json") as fp:
       store.add_metric_json(json.load(fp))

Now we do have a metric - run this again, and you should see it listed.

.. code-block:: python

   print(store.get_metrics())

.. code-block::

   [<ocdsmetricsanalysis.library.Metric object at 0x7f6c812dc390>]

We can quickly list all the observations inside that metric with:

.. code-block:: python

   metric = store.get_metrics()[0]
   observation_list = metric.get_observation_list()
   observations = observation_list.get_data()
   for observation in observations:
       print("OBSERVATION id=" + observation.get_id())
       print(observation.get_measure())
       print(observation.get_dimensions())

You should see something like:

.. code-block::

   OBSERVATION id=1
   46
   {'answer': 'Hate'}
   OBSERVATION id=2
   48
   {'answer': 'Neither hate or like'}
   OBSERVATION id=3
   15
   {'answer': 'Like'}
