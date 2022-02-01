import json
import os

import pytest

from ocdsmetricsanalysis.library import Store


@pytest.fixture
def store(tmpdir) -> Store:
    store = Store(os.path.join(tmpdir, "database.sqlite"))
    source_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "data", "one_dimension.json"
    )
    with open(source_file) as fp:
        data = json.load(fp)
    store.add_metric_json(data)
    return store


def test_observation_list_get_data(store):
    metric = store.get_metric("HATS")
    observation_list = metric.get_observation_list()
    observations = observation_list.get_data()

    assert 3 == len(observations)

    assert "46" == observations[0].get_value_amount()
    assert "Hate" == observations[0].get_dimensions()["answer"]

    assert "48" == observations[1].get_value_amount()
    assert "Neither hate or like" == observations[1].get_dimensions()["answer"]

    assert "15" == observations[2].get_value_amount()
    assert "Like" == observations[2].get_dimensions()["answer"]


def test_observation_list_get_data_by_dimension(store):
    metric = store.get_metric("HATS")
    observation_list = metric.get_observation_list()
    observations_by_dimension = observation_list.get_data_by_dimension("answer")

    assert 3 == len(observations_by_dimension.keys())

    assert 1 == len(observations_by_dimension["Hate"])
    assert "46" == observations_by_dimension["Hate"][0].get_value_amount()

    assert 1 == len(observations_by_dimension["Neither hate or like"])
    assert (
        "48" == observations_by_dimension["Neither hate or like"][0].get_value_amount()
    )

    assert 1 == len(observations_by_dimension["Like"])
    assert "15" == observations_by_dimension["Like"][0].get_value_amount()
