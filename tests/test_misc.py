import os

import pytest

from ocdsmetricsanalysis.exceptions import MetricNotFoundException
from ocdsmetricsanalysis.library import Store


@pytest.fixture
def store(tmpdir) -> Store:
    store = Store(os.path.join(tmpdir, "database.sqlite"))
    return store


def test_add_metric(store):
    store.add_metric("HATS", "Hats", "How many hats?")
    store.get_metric("HATS")
    # Test is just works with no crash


def test_metric_get_json_with_value(store):
    store.add_metric("HATS", "Hats", "How many hats?")
    metric = store.get_metric("HATS")
    metric.add_observation(
        "H1", value_amount="100", value_currency="GBP", dimensions={"colour": "red"}
    )

    assert {
        "description": "How many hats?",
        "id": "HATS",
        "observations": [
            {
                "dimensions": {"colour": "red"},
                "id": "H1",
                "value": {"amount": "100", "currency": "GBP"},
            }
        ],
        "title": "Hats",
    } == metric.get_json()


def test_metric_get_json_with_measure(store):
    store.add_metric("HATS", "Hats", "How many hats?")
    metric = store.get_metric("HATS")
    metric.add_observation("H1", measure="500", dimensions={"colour": "red"})

    assert {
        "description": "How many hats?",
        "id": "HATS",
        "observations": [
            {"dimensions": {"colour": "red"}, "id": "H1", "measure": "500"}
        ],
        "title": "Hats",
    } == metric.get_json()


def test_metric_get_json_with_units(store):
    store.add_metric("HATS", "Hats", "How many hats?")
    metric = store.get_metric("HATS")
    metric.add_observation(
        "H1",
        measure="500",
        dimensions={"colour": "red"},
        unit_name="Hats",
        unit_scheme="InanimateObjects",
        unit_id="HATS",
        unit_uri="http://example.com/InanimateObjects/HATS",
    )

    assert {
        "description": "How many hats?",
        "id": "HATS",
        "observations": [
            {
                "dimensions": {"colour": "red"},
                "id": "H1",
                "measure": "500",
                "unit": {
                    "name": "Hats",
                    "scheme": "InanimateObjects",
                    "id": "HATS",
                    "uri": "http://example.com/InanimateObjects/HATS",
                },
            }
        ],
        "title": "Hats",
    } == metric.get_json()


def test_get_metric_that_does_not_exist(store):
    with pytest.raises(MetricNotFoundException):
        store.get_metric("HATS")


def test_get_metrics(store):
    store.add_metric("HATS", "Hats", "How many hats?")
    store.add_metric("TIES", "Ties", "Why?")
    metrics = store.get_metrics()
    assert 2 == len(metrics)
    assert "HATS" == metrics[0].get_id()
    assert "TIES" == metrics[1].get_id()
