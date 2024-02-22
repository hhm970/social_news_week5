"""This file contains fixtures/stuff used by lots of different tests."""

import pytest
from api import app


@pytest.fixture
def test_client():
    return app.test_client()


@pytest.fixture
def test_empty_stories():
    return list()
