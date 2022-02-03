Example - query data
====================

Setup
-----

Open a python shell in interactive mode (run `python3`) and run the following commands in sequence.

First we'll import the library, make a new store and add some sample data to query.

.. code-block:: python

    from ocdsmetricsanalysis.library import Store
    store = Store("example-query.sqlite")
    store.add_metric("HATS", "How many people like hats?", "We ran a survey to find out.")
    metric = store.get_metric("HATS")
    metric.add_observation("obs1", measure=34, dimensions={'answer':'like'})
    metric.add_observation("obs2", measure=15, dimensions={'answer':'neither like or dislike'})
    metric.add_observation("obs3", measure=12, dimensions={'answer':'dislike'})
    metric.add_observation("obs4", measure=24, dimensions={'answer':'like', 'height': 'tall'})
    metric.add_observation("obs5", measure=10, dimensions={'answer':'like', 'height': 'short'})
    metric.add_observation("obs6", measure=5, dimensions={'answer':'neither like or dislike', 'height': 'tall'})
    metric.add_observation("obs7", measure=10, dimensions={'answer':'neither like or dislike', 'height': 'short'})
    metric.add_observation("obs8", measure=4, dimensions={'answer':'dislike', 'height': 'tall'})
    metric.add_observation("obs9", measure=8, dimensions={'answer':'dislike', 'height': 'short'})

List all observations
---------------------

First we'll do a simple query that lists all the observations.

Every query is done with a Observation List object, which we can easily get.

.. code-block:: python

   observation_list = metric.get_observation_list()

We can at this point set filters and options, but as we want all data we won't do any of that.

Let's just get all the data and print it.


.. code-block:: python

   observations = observation_list.get_data()
   for observation in observations:
       print("OBSERVATION id=" + observation.get_id())
       print(observation.get_measure())
       print(observation.get_dimensions())

You should see a long list of all the data.


.. code-block::

   OBSERVATION id=obs1
   34
   {'answer': 'like'}
   OBSERVATION id=obs2
   15
   {'answer': 'neither like or dislike'}
   OBSERVATION id=obs3
   12
   {'answer': 'dislike'}
   OBSERVATION id=obs4
   24
   {'answer': 'like', 'height': 'tall'}
   OBSERVATION id=obs5
   10
   {'answer': 'like', 'height': 'short'}
   OBSERVATION id=obs6
   5
   {'answer': 'neither like or dislike', 'height': 'tall'}
   OBSERVATION id=obs7
   10
   {'answer': 'neither like or dislike', 'height': 'short'}
   OBSERVATION id=obs8
   4
   {'answer': 'dislike', 'height': 'tall'}
   OBSERVATION id=obs9
   8
   {'answer': 'dislike', 'height': 'short'}



List observations filtered by a dimension
-----------------------------------------

We can see this is a survey about whether people like hats, with the answers further broken down by whether the person responding was tall or short.

Let's say we only care about the opinion of tall people - let's look at that data only.

Get our Observation List object, as before.

.. code-block:: python

   observation_list = metric.get_observation_list()

Set the filter.

.. code-block:: python

   observation_list.filter_by_dimension('height', 'tall')

Now get all data and print it, as before.

.. code-block:: python

   observations = observation_list.get_data()
   for observation in observations:
       print("OBSERVATION id=" + observation.get_id())
       print(observation.get_measure())
       print(observation.get_dimensions())


.. code-block::

   OBSERVATION id=obs4
   24
   {'answer': 'like', 'height': 'tall'}
   OBSERVATION id=obs6
   5
   {'answer': 'neither like or dislike', 'height': 'tall'}
   OBSERVATION id=obs8
   4
   {'answer': 'dislike', 'height': 'tall'}

List observations without a dimension
-------------------------------------

We can see this is a survey about whether people like hats, with the answers further broken down by whether the person responding was tall or short.

However we don't care about the height of the person - we just want to know overall, do people like hats or not?

If we get all observations as above we can see that data, but it is mixed up with other data we don't care about.

Let's filter down just to the data we do care about.

Get our Observation List object, as before.

.. code-block:: python

   observation_list = metric.get_observation_list()

Set the filter - this time we say we don't want any of the other dimensions but the answer.

.. code-block:: python

   observation_list.filter_by_dimension_not_set('height')

Now get all data and print it, as before.

.. code-block:: python

   observations = observation_list.get_data()
   for observation in observations:
       print("OBSERVATION id=" + observation.get_id())
       print(observation.get_measure())
       print(observation.get_dimensions())


.. code-block::

   OBSERVATION id=obs1
   34
   {'answer': 'like'}
   OBSERVATION id=obs2
   15
   {'answer': 'neither like or dislike'}
   OBSERVATION id=obs3
   12
   {'answer': 'dislike'}

This is however a touch inconvenient; you have to know what all the other dimensions are and specifically exclude them. Fortunately there is an easier way to  do this - let's get a new Observation List object and try again.


.. code-block:: python

   observation_list = metric.get_observation_list()

   for key in metric.get_dimension_keys():
       if key != "answer":
            observation_list.filter_by_dimension_not_set(key)

   observations = observation_list.get_data()
   for observation in observations:
       print("OBSERVATION id=" + observation.get_id())
       print(observation.get_measure())
       print(observation.get_dimensions())

You should see exactly the same output as above, but this time we didn't have to know what all the other dimensions were in advance.

Get data by a dimension
-----------------------

Let's say we are a bit curious what tall and short people think, but looking at the long list of answers is hurting our head.

Can we get the observations in handy groups? Yes we can!


Get our Observation List object, as before.

.. code-block:: python

   observation_list = metric.get_observation_list()


This time we'll use the `get_data_by_dimension` function.

.. code-block:: python

   observations_grouped = observation_list.get_data_by_dimension('height')
   for height, observations in observations_grouped.items():
       print("HEIGHT IS " + height)
       for observation in observations:
           print("OBSERVATION id=" + observation.get_id())
           print(observation.get_measure())
           print(observation.get_dimensions())
       print()


.. code-block::

   HEIGHT IS tall
   OBSERVATION id=obs4
   24
  {'answer': 'like', 'height': 'tall'}
   OBSERVATION id=obs6
   5
   {'answer': 'neither like or dislike', 'height': 'tall'}
   OBSERVATION id=obs8
   4
   {'answer': 'dislike', 'height': 'tall'}

   HEIGHT IS short
   OBSERVATION id=obs5
   10
   {'answer': 'like', 'height': 'short'}
   OBSERVATION id=obs7
   10
   {'answer': 'neither like or dislike', 'height': 'short'}
   OBSERVATION id=obs9
   8
   {'answer': 'dislike', 'height': 'short'}
