"""This file contains fixtures/stuff used by lots of different tests."""

import pytest

from app import api


@pytest.fixture
def test_client():
    return api.test_client()
