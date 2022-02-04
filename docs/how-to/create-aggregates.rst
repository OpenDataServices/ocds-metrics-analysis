How to create aggregate data
============================

We want to run a survey about how many people like hats.

Open a python shell in interactive mode (run `python3`) and run the following commands in sequence.

First we'll import the library and make a new store.

.. code-block:: python

    from ocdsmetricsanalysis.library import Store
    store = Store("how-to-create-aggregates.sqlite")

We'll add our own metric.

.. code-block:: python

   store.add_metric("HATS", "How many people like hats?", "We ran a survey to find out.")
   metric = store.get_metric("HATS")

Here are the results of our survey:

.. code-block:: python

   survey_results = [
        {"response":"like", "person_height":"tall"},
        {"response":"like", "person_height":"tall"},
        {"response":"dislike", "person_height":"tall"},
        {"response":"neither like or dislike", "person_height":"tall"},
        {"response":"like", "person_height":"tall"},
        {"response":"neither like or dislike", "person_height":"tall"},
        {"response":"like", "person_height":"short"},
        {"response":"like", "person_height":"short"},
        {"response":"neither like or dislike", "person_height":"short"},
        {"response":"like", "person_height":"short"},
        {"response":"dislike", "person_height":"short"},
        {"response":"neither like or dislike", "person_height":"short"},
        {"response":"like", "person_height":"short"},
        {"response":"dislike", "person_height":"short"},
        {"response":"dislike", "person_height":"short"},
        {"response":"like", "person_height":"short"},
   ]

We don't want to publish individual survey responses in our metrics, as there may be anonymisation issues with that.

Instead, we'll publish aggregates - how many people answered a certain way?

Also, because we have additional data on height, we can break down the answers by height too.

There is a function that will calculate the observations for us automatically.

.. code-block:: python

   metric.add_aggregate_observations(
       survey_results,
       "response",
       "answer",
       idx_to_dimensions={"person_height": {"dimension_name": "height"}}
   )

Lets go through the parameters:

*  `survey_results` is the array of our survey responses.
*  `"response"` is the key in each survey response we are counting the answers to (normally a survey would have more than one question, so we need to know which one to count!)
*  `"answer"` tells us what dimension in the observations we create we should store the answer in.
*  `idx_to_dimensions` tells us about additional questions in the results that we can use to make more dimensions. In this case we are saying the `"person_height"` key in each survey response can be used to make a new dimension called `"height"`.


Let's quickly list all the observations for all overall survey:

.. code-block:: python

   observation_list = metric.get_observation_list()
   observation_list.filter_by_dimension_not_set('height')
   observations = observation_list.get_data()
   for observation in observations:
       print("OBSERVATION id=" + observation.get_id())
       print(observation.get_measure())
       print(observation.get_dimensions())

You should see something like:

.. code-block::

   OBSERVATION id=000000001
   4
   {'answer': 'dislike'}
   OBSERVATION id=000000002
   8
   {'answer': 'like'}
   OBSERVATION id=000000003
   4
   {'answer': 'neither like or dislike'}


Let's also see our results broken down by height:


.. code-block:: python

   observation_list = metric.get_observation_list()
   observations_grouped = observation_list.get_data_by_dimension('height')
   for height, observations in observations_grouped.items():
       print("HEIGHT IS " + height)
       for observation in observations:
           print("OBSERVATION id=" + observation.get_id())
           print(observation.get_measure())
           print(observation.get_dimensions())
       print()

You should see something like:

.. code-block::

   HEIGHT IS short
   OBSERVATION id=000000004
   3
   {'answer': 'dislike', 'height': 'short'}
   OBSERVATION id=000000006
   5
   {'answer': 'like', 'height': 'short'}
   OBSERVATION id=000000008
   2
   {'answer': 'neither like or dislike', 'height': 'short'}

   HEIGHT IS tall
   OBSERVATION id=000000005
   1
   {'answer': 'dislike', 'height': 'tall'}
   OBSERVATION id=000000007
   3
   {'answer': 'like', 'height': 'tall'}
   OBSERVATION id=000000009
   2
   {'answer': 'neither like or dislike', 'height': 'tall'}
