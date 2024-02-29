"""Tests for the social news API"""
import pytest

from psycopg2.extensions import connection

from unittest.mock import patch, MagicMock


# Testing the GET request for "/stories" endpoint
@patch("api.get_database_connection")
@patch("api.loads_stories")
def test_stories_load_successfully(fake_loads_stories, fake_database_connection,
                                   test_database_connection, mock_stories, test_client):

    fake_database_connection = test_database_connection
    fake_loads_stories.fetchall().return_value = mock_stories

    response = test_client.get("/stories")

    assert isinstance(response, list)
    assert response.status_code == 200


@patch("api.get_database_connection")
@patch("api.loads_stories")
def test_load_empty_stories_unsuccessful(fake_loads_stories, fake_database_connection,
                                         test_database_connection, mock_empty_stories, test_client):

    fake_database_connection = test_database_connection
    fake_loads_stories.fetchall().return_value = mock_empty_stories

    response = test_client.get("/stories")

    assert response.status_code == 200


# Testing POST request for "/stories" endpoint
@patch("api.post_new_story")
def post_new_story_successfully(fake_post_new_story, fake_database_connection,
                                test_database_connection, mock_stories, test_client):

    n = len(mock_stories)

    fake_database_connection = test_database_connection

    response = test_client.post(
        "/stories", json={"url": "www.hi.com", "title": "HI"})

    data = response.json

    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) == n + 1
