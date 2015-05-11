import json

from flask import request, Response, url_for
from jsonschema import validate, ValidationError

import models
import decorators
from posts import app
from database import session


# JSON Schema describing structure of a post
post_schema = {
    "properties": {
        "title": {"type": "string"},
        "body": {"type": "string"}
    },
    "required": ["title", "body"]
}




    
# Returning all posts/or all with a query string in the title

@app.route("/api/posts", methods=["GET"])
@decorators.accept("application/json")
def posts_get():
    """  Endpoint to retreive blog posts """

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


# Posting a blog post to the database

@app.route("/api/posts", methods=["POST"])
@decorators.accept("application/json")
@decorators.require("application/json")
def posts_put():
    """  Endpoint to post blog posts """

    # Construct the request data object
    data = request.json
    
    # First validate data object is valid JSON
    # If not valid return 422 error
    try:
        validate(data, post_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")        

    
    # Create data object from the request 
    data = request.json

    # Post data object to database
    post = models.Post(title=data["title"], body=data["body"])
    session.add(post)
    session.commit()

    # Response to client of successful post
    data = json.dumps(post.as_dictionary())
    headers = {"Location": url_for("post_get", id=post.id)}
    return Response(data, 201, headers=headers,
                    mimetype="application/json")

 

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