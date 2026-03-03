import copy

import pytest
from fastapi.testclient import TestClient

from src import app as _app_module


@pytest.fixture(autouse=True)
def reset_activities():
    """Ensure the in-memory activities dict is reset before each test.

    We deep copy the original data and restore it after the test runs.  This
    allows tests to mutate `src.app.activities` without leaking state between
    examples.
    """
    original = copy.deepcopy(_app_module.activities)
    yield
    # restore after test completes
    _app_module.activities.clear()
    _app_module.activities.update(original)


@pytest.fixture

def client():
    """FastAPI TestClient instance for use within tests."""
    return TestClient(_app_module.app)
