"""This file contains fixtures/stuff used by lots of different tests."""
import pytest

from api import app, get_db_connection


@pytest.fixture
def test_client():
    return app.test_client()


@pytest.fixture
def test_database_connection():
    """Return a connection to our Test Database"""

    # Run before the test
    test_config = {
        "DB_HOST": "localhost",
        "DB_PORT": 5000,
        "DB_USER": "howardman",
        "DB_NAME": "social_news",
    }

    conn = get_db_connection(test_config)

    # Passed to the test
    yield conn

    # Run after the test
    with conn.cursor() as cur:
        cur.execute("TRUNCATE message RESTART IDENTITY;")

    conn.commit()
    conn.close()


@pytest.fixture
def mock_stories():
    """A mock stories database"""
    return [
        {"created_at": "Fri, 24 Jun 2022 17:25:16 GMT",
         "id": 1,
         "score": 42,
         "title": "Me and my friends",
         "updated_at": "Fri, 24 Jun 2022 17:25:16 GMT",
         "url": "www.justchilling.com"},
        {"created_at": "Fri, 24 Jun 2022 17:25:16 GMT",
         "id": 2,
         "score": 60,
         "title": "Eating and drinking good food all day",
         "updated_at": "Fri, 24 Jun 2022 17:25:16 GMT",
         "url": "www.bingchilling.com"}
    ]


@pytest.fixture
def mock_empty_stories():
    """An empty mock stories database"""
    return []
