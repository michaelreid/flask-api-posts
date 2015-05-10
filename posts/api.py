import json

from flask import request, Response, url_for
from jsonschema import validate, ValidationError

import models
import decorators
from posts import app
from database import session


    
# Returning all posts/or all with a query string in the title

@app.route("/api/posts", methods=["GET"])
@decorators.accept("application/json")
def posts_get():
    """  Get a list of posts """

    # Construct a query object from query string for title
    title_like = request.args.get("title_like")

    # Construct a query object from query string for body
    body_like = request.args.get("body_like")
    

    # Pass the query object to database and return all posts if available
    posts = session.query(models.Post)
    if title_like and body_like:
        posts = posts.filter(models.Post.title.contains(title_like)). \
                filter(models.Post.body.contains(body_like))
        
    elif title_like:
        posts = posts.filter(models.Post.title.contains(title_like))
        
    elif body_like:
        posts = posts.filter(models.Post.body.contains(body_like))

    else:
        posts = posts.all()

    # Convert posts to JSON format and return response
    data = json.dumps([post.as_dictionary() for post in posts])
    return Response(data, 200, mimetype="application/json")

    



# Returning a single post
    
@app.route("/api/posts/<int:id>", methods=["GET"])
@decorators.accept("application/json")
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



# Deleting a single post

@app.route("/api/post/<int:id>", methods=["DELETE"])
@decorators.accept("application/json")
def post_delete(id):
    """  Delete single post endpoint """

    # Get post from database if exits
    post = session.query(models.Post).get(id)
    
    # Check if post exists
    # If not return 404 with a helpful message
    if not post:
        message = "Could not find post with id {}".format(id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    # Delete post with <id> from database
    session.delete(post)
    session.commit()
        
    # Confirm post deleted
    message = "Deleted post with id {} from the database".format(id)
    data = json.dumps({"message": message})
    return Response(data, 200, mimetype="application/json")