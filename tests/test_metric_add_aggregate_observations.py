import os

import pytest

from ocdsmetricsanalysis.library import Store


@pytest.fixture
def store(tmpdir) -> Store:
    store = Store(os.path.join(tmpdir, "database.sqlite"))
    return store


def test_no_dimensions(store):
    store.add_metric("HATS", "Hats", "How many hats?")
    metric = store.get_metric("HATS")
    metric.add_aggregate_observations(
        [
            {"like_answer": "yes"},
            {"like_answer": "no"},
            {"like_answer": "no"},
            {"like_answer": "yes"},
            {"like_answer": "yes"},
        ],
        "like_answer",
        "answer",
    )

    observation_list = metric.get_observation_list()
    observations = observation_list.get_data()

    assert 2 == len(observations)

    assert "2" == observations[0].get_value_amount()
    assert "no" == observations[0].get_dimensions()["answer"]

    assert "3" == observations[1].get_value_amount()
    assert "yes" == observations[1].get_dimensions()["answer"]
