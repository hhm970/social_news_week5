from datetime import datetime
import psycopg2
from flask import Flask, current_app, jsonify, request
import json


app = Flask(__name__)


def loads_stories(filename: str) -> list[dict]:
    file = open(filename, "r")
    content = file.read()
    file.close()
    return json.loads(content)


def get_current_id(stories: list[dict]) -> int:
    id = len(stories) + 1
    return id


def search_story_results(stories: list[dict],
                         search: str) -> list:
    result = [story for story in stories
              if search in story["title"]]

    return result


def create_new_story(stories: list[dict], url: str,
                     title: str) -> dict:
    new_story = {
        "score": 0,
        "created_at": datetime.strftime(
            datetime.now(), "%a, %d %b %Y %X %Z"),
        "updated_at": datetime.strftime(
            datetime.now(), "%a, %d %b %Y %X %Z"),
        "id": get_current_id(stories),
        "url": url,
        "title": title
    }

    return new_story


def get_order_sort_search(output: list, sorting_criteria: str,
                          order: str = "ascending") -> list:
    if order is None or order == "ascending":
        search_result = sorted(output,
                               key=lambda x:
                               x[sorting_criteria]
                               )

    elif order == "descending":
        search_result = sorted(output,
                               key=lambda x:
                               x[sorting_criteria],
                               reverse=True)

    return search_result


def update_story_score(direction: str,
                       score: int) -> None:
    if direction == "up":
        score += 1
    else:
        score -= 1
    last_updated = datetime.strftime(
        datetime.now(),
        "%a, %d %b %Y %X %Z")

    return (score, last_updated)


def get_sorting_criteria_from_sort(sort: str) -> str | None:
    sort_dict = {"title": "title", "score": "score",
                 "created": "created_at", "modified": "modified_at"}

    if sort is None:
        return "created_at"

    return sort_dict.get(sort)


@app.route("/", methods=["GET"])
def index():
    return current_app.send_static_file("index.html")


@app.route("/add", methods=["GET"])
def addstory():
    return current_app.send_static_file("./addstory/index.html")


@app.route("/scrape", methods=["GET"])
def scrape():
    return current_app.send_static_file("./scrape/index.html")


@app.route("/stories", methods=["GET", "POST"])
def get_stories():
    """
    GET: Retrieves all available stories on the API, or 
    searches up for stories with a given title and orders them.
    POST: Adds a new story onto the API.
    """
    args = request.args.to_dict()
    search = args.get("search")
    sort = args.get("sort")
    order = args.get("order")

    if request.method == "GET":

        stories = loads_stories("stories.json")

        # Consider the case where we have no 'search' query parameter.
        if search is None:
            # Consider the edge case where there are no stories.
            if len(stories) == 0:
                return jsonify({"error": True, "message":
                                "No stories were found"
                                }), 404

            output = stories

        else:
            result = search_story_results(stories, search)

            if len(result) == 0:
                return jsonify({"error": True, "message":
                                "No stories were found"
                                }), 404

            output = result

        # Consider the 'sort' query parameter
        sorting_criteria = get_sorting_criteria_from_sort(sort)

        if sorting_criteria is None:
            return jsonify({"error": True, "message":
                            "'sort' query parameter takes values 'title', 'score', 'created', 'modified'"
                            }), 400

        if order is None or order in {"ascending", "descending"}:
            return jsonify(get_order_sort_search
                           (output, sorting_criteria, order)
                           ), 200

        else:
            return jsonify({"error": True, "message":
                            "'order' query parameter only takes values 'ascending', 'descending'"
                            }), 400

    elif request.method == "POST":
        data = request.json

        if (data.get("url") or data.get("title")) == None:
            return jsonify(
                {"error": True, "message":
                 "'title' and 'url' of new story need to be specified"
                 }), 400

        stories = loads_stories("stories.json")

        stories.append(create_new_story(
            stories, data.get("url"), data.get("title")))

        return jsonify(stories), 201


@app.route("/stories/<int:id>", methods=["PATCH", "DELETE"])
def existing_stories_id(id):
    """
    PATCH: Edits an existing story on the API
    DELETE: Deletes an existing story on the API
    """

    stories = loads_stories("stories.json")

    if id <= 0 or id > len(stories):
        return jsonify({"error": True, "message":
                        f"'id' can only be between 0 and {len(stories)}"
                        }), 404

    if request.method == "PATCH":

        data = request.json

        if (data.get("url") or data.get("title")) is None:
            return jsonify({"error": True, "message":
                            "'title' and 'url' of new story need to be specified"
                            }), 400

        for story in stories:
            if story["id"] == id:
                story["url"] = data.get("url")
                story["title"] = data.get("title")

        return jsonify(stories), 201

    elif request.method == "DELETE":

        for story in stories:
            if story["id"] == id:
                stories.remove(story)

        return jsonify(stories), 200


@app.route("/stories/<int:id>/votes", methods=["POST"])
def post_vote_stories(id):
    """Raises the vote of a story by 1"""

    data = request.json
    stories = loads_stories("stories.json")

    if id <= 0 or id > len(stories):
        return jsonify({"error": True, "message":
                        f"'id' can only be between 0 and {len(stories)}"
                        }), 404

    if request.method == "POST":

        for story in stories:
            if story["id"] == id:
                direction = data["direction"]
                score = story["score"]
                if direction not in {"up", "down"}:
                    return jsonify({"error": True,
                                    "message":
                                    "'direction' only takes 'up', 'down' as values"
                                    })
                if direction == "down" and score == 0:
                    return jsonify({"error": True,
                                    "message":
                                    "Can't downvote for a story with a score of 0"
                                    }), 400
                story["score"] = update_story_score[0]
                story["updated_at"] = update_story_score[1]

    return jsonify(stories), 201


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
