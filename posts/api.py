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
    data = json.dumps([])
    return Response(data, 200, mimetype="application/json")