import json
import os

import pytest

from ocdsmetricsanalysis.library import Store


@pytest.fixture
def store(tmpdir) -> Store:
    store = Store(os.path.join(tmpdir, "database.sqlite"))
    source_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "data", "two_dimensions.json"
    )
    with open(source_file) as fp:
        data = json.load(fp)
    store.add_metric_json(data)
    return store


def test_observation_list_get_data(store):
    metric = store.get_metric("HATS")
    observation_list = metric.get_observation_list()
    observations = observation_list.get_data()

    assert 6 == len(observations)

    assert "46" == observations[0].get_value_amount()
    assert "Hate" == observations[0].get_dimensions()["answer"]
    assert "tall" == observations[0].get_dimensions()["height"]

    assert "48" == observations[1].get_value_amount()
    assert "Neither hate or like" == observations[1].get_dimensions()["answer"]
    assert "tall" == observations[1].get_dimensions()["height"]

    assert "15" == observations[2].get_value_amount()
    assert "Like" == observations[2].get_dimensions()["answer"]
    assert "tall" == observations[2].get_dimensions()["height"]

    assert "36" == observations[3].get_value_amount()
    assert "Hate" == observations[3].get_dimensions()["answer"]
    assert "short" == observations[3].get_dimensions()["height"]

    assert "45" == observations[4].get_value_amount()
    assert "Neither hate or like" == observations[4].get_dimensions()["answer"]
    assert "short" == observations[4].get_dimensions()["height"]

    assert "31" == observations[5].get_value_amount()
    assert "Like" == observations[5].get_dimensions()["answer"]
    assert "short" == observations[5].get_dimensions()["height"]


def test_observation_list_filter_by_dimension_then_get_data(store):
    metric = store.get_metric("HATS")
    observation_list = metric.get_observation_list()
    observation_list.filter_by_dimension("height", "tall")
    observations = observation_list.get_data()

    assert 3 == len(observations)

    assert "46" == observations[0].get_value_amount()
    assert "Hate" == observations[0].get_dimensions()["answer"]
    assert "tall" == observations[0].get_dimensions()["height"]

    assert "48" == observations[1].get_value_amount()
    assert "Neither hate or like" == observations[1].get_dimensions()["answer"]
    assert "tall" == observations[1].get_dimensions()["height"]

    assert "15" == observations[2].get_value_amount()
    assert "Like" == observations[2].get_dimensions()["answer"]
    assert "tall" == observations[2].get_dimensions()["height"]


def test_observation_list_filter_by_dimension_twice_then_get_data(store):
    """Filter_by_dimension twice on 2 different dimensions then get data.
    Makes sure you can apply more than one filter with no problems."""
    metric = store.get_metric("HATS")
    observation_list = metric.get_observation_list()
    observation_list.filter_by_dimension("answer", "Hate")
    observation_list.filter_by_dimension("height", "tall")
    observations = observation_list.get_data()

    assert 1 == len(observations)

    assert "46" == observations[0].get_value_amount()
    assert "Hate" == observations[0].get_dimensions()["answer"]
    assert "tall" == observations[0].get_dimensions()["height"]


def test_observation_list_get_data_by_dimension(store):
    metric = store.get_metric("HATS")
    observation_list = metric.get_observation_list()
    observations_by_dimension = observation_list.get_data_by_dimension("answer")

    assert 3 == len(observations_by_dimension.keys())

    assert 2 == len(observations_by_dimension["Hate"])
    assert "46" == observations_by_dimension["Hate"][0].get_value_amount()
    assert "36" == observations_by_dimension["Hate"][1].get_value_amount()

    assert 2 == len(observations_by_dimension["Hate"])
    assert (
        "48" == observations_by_dimension["Neither hate or like"][0].get_value_amount()
    )
    assert (
        "45" == observations_by_dimension["Neither hate or like"][1].get_value_amount()
    )

    assert 2 == len(observations_by_dimension["Hate"])
    assert "15" == observations_by_dimension["Like"][0].get_value_amount()
    assert "31" == observations_by_dimension["Like"][1].get_value_amount()


def test_metric_get_dimension_keys(store):
    metric = store.get_metric("HATS")
    keys = metric.get_dimension_keys()

    assert 2 == len(keys)

    assert "answer" == keys[0]
    assert "height" == keys[1]


def test_units(store):
    metric = store.get_metric("HATS")
    observation_list = metric.get_observation_list()
    observations = observation_list.get_data()

    assert 6 == len(observations)

    for i in range(0, 6):
        assert not observations[i].has_unit()
