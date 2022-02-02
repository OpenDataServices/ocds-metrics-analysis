import json
import os

import pytest

from ocdsmetricsanalysis.library import Store


@pytest.fixture
def store(tmpdir) -> Store:
    store = Store(os.path.join(tmpdir, "database.sqlite"))
    source_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "data",
        "one_and_two_dimensions.json",
    )
    with open(source_file) as fp:
        data = json.load(fp)
    store.add_metric_json(data)
    return store


def test_observation_list_1(store):
    """Use filter_by_dimension_not_set to only get one result"""
    metric = store.get_metric("HATS")
    observation_list = metric.get_observation_list()
    observation_list.filter_by_dimension_not_set("height")
    observations = observation_list.get_data()

    assert 1 == len(observations)

    assert "46" == observations[0].get_measure()
    assert {"answer": "Like"} == observations[0].get_dimensions()


def test_observation_list_2(store):
    """Use filter_by_dimension_not_set to only get one result.
    Also use filter_by_dimension, make sure we still get one result & both filters work together."""
    metric = store.get_metric("HATS")
    observation_list = metric.get_observation_list()
    observation_list.filter_by_dimension_not_set("height")
    observation_list.filter_by_dimension("answer", "Like")
    observations = observation_list.get_data()

    assert 1 == len(observations)

    assert "46" == observations[0].get_measure()
    assert {"answer": "Like"} == observations[0].get_dimensions()


def test_observation_list_3(store):
    """Use filter_by_dimension_not_set and filter_by_dimension to request data that does not exist.
    Make sure both filters work together."""
    metric = store.get_metric("HATS")
    observation_list = metric.get_observation_list()
    observation_list.filter_by_dimension_not_set("height")
    observation_list.filter_by_dimension("answer", "Hate")
    observations = observation_list.get_data()

    assert 0 == len(observations)
