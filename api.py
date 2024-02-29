"""
WEEK 4 COURSEWORK
-----------------
Module Name: api.py

Description:
This py file is designed to act as a server to 
a social news API. Functionalities include 
• Searching for new articles via GET requests, 
• Adding new articles via POST requests, 
• Editing existing articles via PATCH requests, 
• Deleting existing articles via DELETE requests.

This project incorporates REST architecture into the API,
and is designed to be run within a virtual environment, 
the modules of which are included in requirements.txt

Author: Howard Man
"""


import psycopg2
import psycopg2.extras
from flask import Flask, current_app, jsonify, request
from psycopg2 import sql
from psycopg2.extensions import connection


app = Flask(__name__)


def get_db_connection() -> connection:
    """Creates a connection from our API to the social_news database"""
    return psycopg2.connect("dbname=social_news user=howardman host=localhost")


def fetch_scores(conn: connection) -> list[dict[str, any]]:
    """
    Fetches scores for all stories whose story_id are 
    in the votes table
    """
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute(sql.SQL("""SELECT stories.*, SUM(CASE direction WHEN 'up' THEN 1 ELSE -1 END)
                        AS score
                        FROM stories
                        JOIN votes
                        ON (stories.id = votes.story_id) 
                        WHERE stories.id = votes.story_id
                        GROUP BY stories.id"""))


def loads_stories(conn: connection, sort_by: str, order_by: str, search: str) -> list[dict[str, any]]:
    """
    Loads the content within the stories database,
    with an option for customising sort, order, and search
    """

    if search is None:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute(sql.SQL("""SELECT * FROM stories ORDER BY {} {}""")
                    .format(sql.Identifier(sort_by), sql.SQL(order_by)))

    else:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute(
            sql.SQL("""SELECT * FROM stories 
                    WHERE title ILIKE '%{}%' 
                    ORDER BY {} {}""").format(sql.SQL(search), sql.Identifier(sort_by), sql.SQL(order_by)))

    rows = cur.fetchall()
    conn.commit()
    cur.close()
    return rows


def get_highest_id(conn: connection) -> int:
    """Returns the highest id number within a list of stories"""
    sort_by = 'id'
    order_by = 'DESC'

    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql.SQL("""SELECT id FROM stories ORDER BY {} {} LIMIT 1""")
                .format(sql.Identifier(sort_by), sql.SQL(order_by))
                )

    rows = cur.fetchone()
    conn.commit()
    cur.close()
    return rows.get("id")


def post_new_story(conn: connection, url: str, title: str) -> list[dict[str, any]]:
    """Adds new story into social_news database, returning the updated
    social_news database"""
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute(sql.SQL("""INSERT INTO stories (title, url, created_at, updated_at)
                        VALUES (%s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"""
                        ), (title, url)
                )

    cur.execute(sql.SQL("""SELECT * FROM stories"""))

    rows = cur.fetchall()
    conn.commit()
    cur.close()
    return rows


def valid_input_id_test(conn: connection, id: int) -> bool:
    """Criteria for checking whether a story id is valid"""
    max_id = get_highest_id(conn)
    if not isinstance(id, int):
        return "id_not_int"
    if id <= 0 or id > max_id:
        return "id_not_in_range"
    return True


def patch_existing_story(conn: connection, url: str, title: str, id: int) -> list[dict[str, any]]:
    """Edits the url and title of a row in the stories table via a PATCH request"""
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute(sql.SQL("""UPDATE stories
                        SET url = %s,
                        title = %s
                        WHERE id = %s"""), (url, title, id))

    cur.execute(sql.SQL("""SELECT * FROM stories"""))

    rows = cur.fetchall()
    conn.commit()
    cur.close()
    return rows


def delete_existing_story(conn: connection, id: int) -> list[dict[str, any]]:
    """Deletes an existing story in stories database"""
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute(sql.SQL("""DELETE FROM stories
                        WHERE id = %s"""), (id, )
                )

    cur.execute(sql.SQL("""SELECT * FROM stories"""))

    rows = cur.fetchall()
    conn.commit()
    cur.close()
    return rows


def find_story_by_id(conn: connection, id: int):
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute(sql.SQL("""SELECT * FROM stories WHERE id = %s"""),
                (id, )
                )

    rows = cur.fetchone()
    conn.commit()
    cur.close()
    return rows


def update_story_date(conn: connection, id: int) -> list[dict[str, any]]:
    """
    Updates the updated_at field of a story to the stories table 
    after an upvote/downvote
    """

    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute(sql.SQL("""UPDATE stories
                        SET updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s"""), (id, ))

    cur.execute(sql.SQL("""SELECT * FROM stories"""))

    rows = cur.fetchall()
    conn.commit()
    cur.close()
    return rows


def create_new_votes_record(conn: connection, id: int, direction: str) -> None:
    """Creates a new row in the votes table"""

    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute(sql.SQL("""INSERT INTO votes (direction, created_at, updated_at, story_id)
                        VALUES (%s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, %s)"""), (direction, id))


# ===============================================================================================================
# ================================= API ROUTES ==================================================================
# ===============================================================================================================


@app.route("/", methods=["GET"])
def index():
    return current_app.send_static_file("index.html")


@app.route("/add", methods=["GET"])
def addstory():
    """Adds story via frontend"""
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
    if request.method == "GET":
        sort_by = request.args.get('sort_by', default='id')
        order_by = request.args.get('order_by', default='ASC').upper()
        search = request.args.get('search', default=None)

        data = loads_stories(conn, sort_by, order_by, search)
        if len(data) == 0:
            return jsonify({"error": True,
                            "message": "No results found for your search."}), 400

        return data, 200

    if request.method == "POST":
        data = request.json
        url = data.get("url")
        title = data.get("title")

        if url is None or title is None:
            return jsonify(
                {"error": True,
                    "message": "'title' and 'url' of new story need to be specified"}), 400

        data = post_new_story(conn, url, title)

        return data, 201

    return jsonify(
        {"error": True, "message": "Only methods GET and POST are available."}), 404


@app.route("/stories/<int:id>", methods=["PATCH", "DELETE"])
def existing_stories_id(id: int):
    """
    PATCH: Edits an existing story on the API
    DELETE: Deletes an existing story on the API
    """

    if not valid_input_id_test(conn, id):
        return jsonify({"error": True, "message": "Inputted 'id' not valid"}), 400

    if request.method == "PATCH":
        data = request.json
        url = data.get("url")
        title = data.get("title")

        if url is None or title is None:
            return jsonify(
                {"error": True, "message": "'title' and 'url' of new story need to be specified"}), 400

        data = patch_existing_story(conn, url, title, id)

        return data, 201

    if request.method == "DELETE":
        data = delete_existing_story(conn, id)

        return data, 200

    return jsonify(
        {"error": True, "message": "Only methods PATCH AND DELETE are available."}), 404


@app.route("/stories/<int:id>/votes", methods=["POST"])
def post_vote_stories(id: int):
    """Raises the vote of a story by 1"""

    if valid_input_id_test(conn, id) == "id_not_int":
        return jsonify(
            {"error": True, "message": "'id' needs to be an integer"}), 400
    if valid_input_id_test(conn, id) == "id_not_in_range":
        return jsonify(
            {"error": True, "message": "No stories with this id"}), 400

    if request.method == "POST":
        data = request.json
        direction = data.get("direction")

        if direction not in {"up", "down"}:
            return jsonify({
                "error": True, "message": "'direction' only takes 'up', 'down' as values"
            }), 400

        create_new_votes_record(conn, id, direction)

        data = update_story_date(conn, id)

        return data, 200

    return {"error": True, "message": "Only method POST is available."}, 404


if __name__ == "__main__":
    try:
        conn = get_db_connection()
    except:
        print("Not able to establish a connection to database.")
    else:
        app.run(debug=True, host="0.0.0.0", port=5000)
