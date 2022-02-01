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


def test_get_metric_that_does_not_exist(store):
    with pytest.raises(MetricNotFoundException):
        store.get_metric("HATS")
