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

    assert "2" == observations[0].get_measure()
    assert "no" == observations[0].get_dimensions()["answer"]

    assert "3" == observations[1].get_measure()
    assert "yes" == observations[1].get_dimensions()["answer"]


def test_one_dimension(store):
    store.add_metric("HATS", "Hats", "How many hats?")
    metric = store.get_metric("HATS")
    metric.add_aggregate_observations(
        [
            {"like_answer": "yes", "height_answer": "tall"},
            {"like_answer": "no", "height_answer": "tall"},
            {"like_answer": "no", "height_answer": "tall"},
            {"like_answer": "yes", "height_answer": "short"},
            {"like_answer": "yes", "height_answer": "short"},
        ],
        "like_answer",
        "answer",
        idx_to_dimensions={"height_answer": {"dimension_name": "height"}},
    )

    observation_list = metric.get_observation_list()
    observations = observation_list.get_data()

    assert 6 == len(observations)

    expected_answers = [
        ("2", "no", None),
        ("3", "yes", None),
        ("0", "no", "short"),
        ("2", "no", "tall"),
        ("2", "yes", "short"),
        ("1", "yes", "tall"),
    ]
    for expected_answer in expected_answers:
        observation = observations.pop(0)
        assert (
            expected_answer[0] == observation.get_measure()
        ), "EXPECTED ANSWER = " + str(expected_answer)
        assert (
            expected_answer[1] == observation.get_dimensions()["answer"]
        ), "EXPECTED ANSWER = " + str(expected_answer)
        assert expected_answer[2] == observation.get_dimensions().get(
            "height"
        ), "EXPECTED ANSWER = " + str(expected_answer)


def test_two_dimensions(store):
    store.add_metric("HATS", "Hats", "How many hats?")
    metric = store.get_metric("HATS")
    metric.add_aggregate_observations(
        [
            {"like_answer": "yes", "height_answer": "tall", "hair_answer": "lots"},
            {"like_answer": "no", "height_answer": "tall", "hair_answer": "lots"},
            {"like_answer": "no", "height_answer": "tall", "hair_answer": "lots"},
            {"like_answer": "yes", "height_answer": "short", "hair_answer": "none"},
            {"like_answer": "yes", "height_answer": "short", "hair_answer": "lots"},
        ],
        "like_answer",
        "answer",
        idx_to_dimensions={
            "height_answer": {"dimension_name": "height"},
            "hair_answer": {"dimension_name": "hair"},
        },
    )

    observation_list = metric.get_observation_list()
    observations = observation_list.get_data()

    assert 18 == len(observations)

    expected_answers = [
        ("2", "no", None, None),
        ("3", "yes", None, None),
        ("0", "no", "short", None),
        ("2", "no", "tall", None),
        ("2", "yes", "short", None),
        ("1", "yes", "tall", None),
        ("2", "no", None, "lots"),
        ("0", "no", None, "none"),
        ("2", "yes", None, "lots"),
        ("1", "yes", None, "none"),
        ("0", "no", "short", "lots"),
        ("0", "no", "short", "none"),
        ("2", "no", "tall", "lots"),
        ("0", "no", "tall", "none"),
        ("1", "yes", "short", "lots"),
        ("1", "yes", "short", "none"),
        ("1", "yes", "tall", "lots"),
        ("0", "yes", "tall", "none"),
    ]
    for expected_answer in expected_answers:
        observation = observations.pop(0)
        assert (
            expected_answer[0] == observation.get_measure()
        ), "EXPECTED ANSWER = " + str(expected_answer)
        assert (
            expected_answer[1] == observation.get_dimensions()["answer"]
        ), "EXPECTED ANSWER = " + str(expected_answer)
        print(observation.get_dimensions())
        assert expected_answer[2] == observation.get_dimensions().get(
            "height"
        ), "EXPECTED ANSWER = " + str(expected_answer)
        assert expected_answer[3] == observation.get_dimensions().get(
            "hair"
        ), "EXPECTED ANSWER = " + str(expected_answer)
