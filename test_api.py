"""Tests for the social news API"""

from unittest.mock import patch, MagicMock


# Testing the GET request for "/stories" endpoint
def test_loads_stories_return_200(test_client):

    response = test_client.get("/stories")

    assert response.status_code == 200
    assert isinstance(response.json, list)


def test_get_search_no_results_stories_404(test_client):

    response = test_client.get(
        "/stories?search=hiasdahjfdkjbsadkjabsdkjbnaskjdnaksjdn")

    assert response.status_code == 404
    assert response.json == {"error": True, "message": "No stories were found"}


def test_get_multiple_searches_from_stories(test_client):

    response = test_client.get(
        "/stories?search=and&sort=title&order=descending")

    assert response.status_code == 200
    assert response.json == [
        {
            "created_at": "Fri, 24 Jun 2022 17:25:16 GMT",
            "id": 7,
            "score": 313,
            "title": "Willow Project: US government approves Alaska oil and gas development",
            "updated_at": "Fri, 24 Jun 2022 17:25:16 GMT",
            "url": "https://www.bbc.co.uk/news/world-us-canada-64943603"
        },
        {
            "created_at": "Fri, 24 Jun 2022 17:25:16 GMT",
            "id": 1,
            "score": 42,
            "title": "Voters Overwhelmingly Back Community Broadband in Chicago and Denver",
            "updated_at": "Fri, 24 Jun 2022 17:25:16 GMT",
            "url": "https://www.vice.com/en/article/xgzxvz/voters-overwhelmingly-back-community-broadband-in-chicago-and-denver"
        },
        {
            "created_at": "Fri, 24 Jun 2022 17:25:16 GMT",
            "id": 8,
            "score": 2,
            "title": "SVB and Signature Bank: How bad is US banking crisis and what does it mean?",
            "updated_at": "Fri, 24 Jun 2022 17:25:16 GMT",
            "url": "https://www.bbc.co.uk/news/business-64951630"
        },
        {
            "created_at": "Fri, 24 Jun 2022 17:25:16 GMT",
            "id": 3,
            "score": 471,
            "title": "Karen Gillan teams up with Lena Headey and Michelle Yeoh in assassin thriller Gunpowder Milkshake",
            "updated_at": "Fri, 24 Jun 2022 17:25:16 GMT",
            "url": "https://www.empireonline.com/movies/news/gunpowder-milk-shake-lena-headey-karen-gillan-exclusive/"
        },
        {
            "created_at": "Fri, 24 Jun 2022 17:25:16 GMT",
            "id": 9,
            "score": 128,
            "title": "Aukus deal: Summit was projection of power and collaborative intent",
            "updated_at": "Thu, 15 Feb 2024 16:14:03 ",
            "url": "https://www.bbc.co.uk/news/uk-politics-64948535"
        }
    ]


def test_get_search_sort_error_400(test_client):

    response = test_client.get(
        "/stories?search=and&sort=what")

    assert response.status_code == 400
    assert response.json == {
        "error": True, "message":
        "'sort' query parameter takes values 'title', 'score', 'created', 'modified'"}


def test_get_search_order_default_asc(test_client):

    response1 = test_client.get("/stories?search=and&sort=title")
    response2 = test_client.get(
        "/stories?search=and&sort=title&order=ascending")

    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response1.json == response2.json


def test_get_search_order_error_400(test_client):

    response = test_client.get("/stories?search=and&sort=title&order=nothing!")

    assert response.status_code == 400
    assert response.json == {"error": True, "message":
                             "'order' query parameter only takes values 'ascending', 'descending'"
                             }


# Testing POST request for "/stories" endpoint

def test_post_no_url_error_400(test_client):
    response = test_client.post("/stories", json={
        "url": None,
        "title": None
    })

    assert response.status_code == 400
    assert response.json == {"error": True, "message":
                             "'title' and 'url' of new story need to be specified"
                             }


def test_post_new_story_201(test_client):
    response = test_client.post("/stories", json={
        "url": "www.google.com",
        "title": "GOOGLE"
    })

    assert response.status_code == 201


def test_patch_story_error_404(test_client):
    response = test_client.patch("/stories/-1", json={
        "url": "www.google.com",
        "title": "GOOGLE"
    })

    assert response.status_code == 404


def test_patch_story_200(test_client):
    response = test_client.patch("/stories/1", json={
        "url": "www.google.com",
        "title": "GOOGLE"
    })

    assert response.status_code == 201
