import json

from flask import request, Response, url_for
from jsonschema import validate, ValidationError

import models
import decorators
from posts import app
from database import session

@app.route("/api/posts", methods=["GET"])
def posts_get():
    """  Get a list of posts """

    # Get the posts from the database
    posts = session.query(models.Post).all()

    # Convert to json format
    data = json.dumps([post.as_dictionary() for post in posts])
    return Response(data, 200, mimetype="application/json")



@app.route("/api/posts/<int:id>", methods=["GET"])
def post_get(id):
    """  Single post endpoint """

    # Get post with <id> from database
    post = session.query(models.Post).get(id)


    # Check if post exists
    # If not return 404 with a helpful message
    if not post:
        message = "Could not find post with id {}".format(id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    # Else return post
    data = json.dumps(post.as_dictionary())
    return Response(data, 200, mimetype="application/json")