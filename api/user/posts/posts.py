import base64
from dataclasses import asdict

from flask import Blueprint, jsonify, request
from flask_login import login_required
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError

from api import basic_auth, db
from api.user.author.model import Author
from api.user.comments.model import Comment
from api.user.posts.model import Post
from api.user.relations import author_likes_comments, author_likes_posts
from api.utils import Visibility, get_author_info, get_object_type, get_pagination_params

from flasgger import swag_from
from api.user.posts.docs import *

# note: this blueprint is usually mounted under  URL prefix
posts_bp = Blueprint("posts", __name__)


@posts_bp.route("/<string:author_id>/posts/<string:post_id>", methods=["GET"])
@swag_from(
    {
        "tags": ["Posts"],
        "description": "Returns a single post with id post_id authored by author_id.",
        "parameters": [
            {"in": "path", "name": "author_id", "description": "Id of the author of the post"},
            {"in": "path", "name": "post_id", "description": "Id of the post to fetch"},
        ],
        "responses": {
            200: {"description": "Single post", "schema": post_schema},
            404: {"description": "Author not found or Post not found"},
        },
    }
)
@basic_auth.required
def get_post(author_id: str, post_id: str):
    """Get the public post whose id is post_id from author with id author_id"""
    author = Author.query.filter_by(id=author_id).first_or_404()
    post_search = Post.query.filter_by(id=post_id, author=author.url).first_or_404()

    return post_search.getJSON(), 200


@posts_bp.route("/<string:author_id>/posts/<string:post_id>", methods=["POST"])
@login_required
def edit_post(author_id: str, post_id: str):
    """
    Update the post whose id is POST_ID (must be authenticated) ie the person
    editing the post must be the author of the post.
    json received must have all columns to be updated as key value pairs
    """
    json = request.json

    author = Author.query.filter_by(id=author_id).first_or_404()
    post = Post.query.filter_by(id=post_id, author=author.url, inbox=author.id).first_or_404()

    for k, v in json.items():
        setattr(post, k, v)

    db.session.commit()

    return {"success": 1, "message": "Post edited successfully."}, 201


@posts_bp.route("/<string:author_id>/posts/<string:post_id>", methods=["DELETE"])
@login_required
def delete_post(author_id: str, post_id: str):
    """remove the post whose id is post_id"""
    author = Author.query.filter_by(id=author_id).first_or_404()
    post = Post.query.filter_by(id=post_id, author=author.url, inbox=author_id).first_or_404()

    db.session.delete(post)
    db.session.commit()
    return {"success": 1, "message": "Post deleted successfully."}, 200


@posts_bp.route("/<string:author_id>/posts/<string:post_id>", methods=["PUT"])
@login_required
def create_post(author_id: str, post_id: str):
    """
    Create a new post where its id is post_id.
    Post does not have comments yet.
    """
    return make_post(request.json, author_id, post_id=post_id)


@posts_bp.route("/<string:author_id>/posts", methods=["POST"])
@login_required
def create_post_auto_gen_id(author_id: str):
    """
    Create a new post but generate a new id.
    Arguments:
        author_id: object id of the local/remote author who made or reshared the post.

    The author id/url in the json body is author
    """
    return make_post(request.json, author_id)


@posts_bp.route("/<string:author_id>/posts/", methods=["GET"])
@swag_from(
    {
        "tags": ["Posts"],
        "description": "Returns a recent public posts authored by author_id.",
        "parameters": [
            {"in": "path", "name": "author_id", "description": "Id of the author of the posts"},
        ],
        "responses": {
            200: {"description": "A list of recent posts", "schema": posts_schema},
            404: {"description": "Author not found"},
        },
    }
)
@basic_auth.required
def get_recent_posts(author_id: str):
    """
    Get the recent (PUBLIC) posts from author author_id (paginated).
    Public posts made by author has the inbox and author_id as same.
    """

    author = Author.query.filter_by(id=author_id).first_or_404()
    posts = (
        Post.query.filter_by(inbox=author_id, author=author.url)
        .order_by(desc(Post.published))
        .paginate(**get_pagination_params().dict)
        .items
    )

    return {"type": "posts", "items": [post.getJSON() for post in posts]}, 200


@posts_bp.route("/<string:author_id>/posts/<string:post_id>/image", methods=["GET"])
@swag_from(
    {
        "tags": ["Posts"],
        "description": "Returns a public post containing image authored by author_id with base64 encoded image content.",
        "parameters": [
            {"in": "path", "name": "author_id", "description": "Id of the author of the post"},
            {"in": "path", "name": "post_id", "description": "Id of the image post"},
        ],
        "responses": {
            200: {"description": "Post with image content encoded as base64.", "schema": posts_schema},
            400: {"description": "Not an image"},
            404: {"description": "Author not found or Post not found."},
        },
    }
)
@basic_auth.required
def post_as_base64_img(author_id: str, post_id: str):
    """
    Get the public post converted to binary as an image
    """
    author = Author.query.filter_all(id=author_id).first_or_404()
    post = Post.query.filter_all(author=author.url, id=post_id).first_or_404()
    valid = ["application/base64", "image/png;base64", "image/jpeg;base64"]
    if post.contentType not in valid:
        return "Not an image post", 400

    decoded_img = base64.b64decode(post.content)
    json = post.getJSON()
    json["content"] = decoded_img

    return json


@posts_bp.route("/<string:author_id>/inbox/", methods=["POST"])
@swag_from(
    {
        "tags": ["Likes", "Inbox"],
        "description": "Send a like object to author with author_id (receiver)",
        "consumes": ["application/json"],
        "parameters": [
            {
                "in": "path",
                "name": "author_id",
                "required": "true",
                "description": "Id of the author of the object. Object can be a post or comment.",
                "example": "69abdhgtT420wjsw",
            },
            {"in": "body", "schema": inbox_schema},
        ],
        "responses": {
            201: {
                "description": "Post or comment liked successfully",
                "schema": {"properties": {"message": {"type": "string"}}},
            },
            404: {"description": "Author not found"},
            400: {"description": "Invalid object id"},
        },
    }
)
@basic_auth.required
def send_like(author_id: str):
    """
    Send a like object to author_id.
    Like could be made on either post or comments of the author.
    """
    # Author's inbox must exist on server
    Author.query.filter_by(id=author_id).first_or_404()

    data = request.json
    object_id = data.get("object")
    type = get_object_type(object_id)
    made_by = data.get("author").get("id")
    response = {}
    match type:
        case "comment":
            stmt = author_likes_comments.insert().values(author=made_by, comment=object_id)
            db.session.execute(stmt)
            db.session.commit()
            response = {"message": "Like created"}, 201
        case "post":
            stmt = author_likes_posts.insert().values(author=made_by, post=object_id)
            db.session.execute(stmt)
            db.session.commit()
            response = {"message": "Like created"}, 201
        case None:
            response = {"message": "Invalid object id"}, 400

    return response


@posts_bp.route("/<string:author_id>/posts/<string:post_id>/likes", methods=["GET"])
@swag_from(
    {
        "tags": ["Likes"],
        "description": "Returns a list of likes from other authors on post post_id authored by author_id",
        "parameters": [
            {
                "in": "path",
                "name": "author_id",
                "description": "Id of the author who posted post post_id",
                "required": "true",
            },
            {
                "in": "path",
                "name": "post_id",
                "description": "Id of the post to get the list of likes from",
                "required": "true",
            },
        ],
        "responses": {
            200: {"description": "A list of likes", "schema": likes_schema},
            404: {"description": "Author or post not found"},
        },
    }
)
@basic_auth.required
def get_likes(author_id: str, post_id: str):
    """Get a list of likes from other authors on author_id’s post post_id"""
    # Author, post must exist on our server otherwise invalid request
    author = Author.query.filter_by(id=author_id).first_or_404()
    post = Post.query.filter_by(author=author.url, id=post_id).first_or_404()

    # fetch all author urls who like this post from database
    stmt = author_likes_posts.select().where(author_likes_posts.c.post == post.url)
    result = db.session.execute(stmt)
    authors = result.all()
    authors = [getattr(row, "author") for row in authors]

    # Generating likes
    likes = []
    for author_url in authors:
        author = get_author_info(author_url)

        # If the author (remote) has been deleted from there server
        # or does not exist then we skip that like (TODO should we delete such a like)
        if not author:
            continue

        name = author.get("displayName")
        summary = name + "likes your post." if name else ""
        like = {"type": "like", "author": author, "object": post.url, "summary": summary}

        likes.append(like)

    return {"type": "likes", "items": likes}, 200


@posts_bp.route("/<string:author_id>/liked", methods=["GET"])
@swag_from(
    {
        "tags": ["Likes"],
        "description": "Returns a list of objects liked by author with author_id",
        "parameters": [
            {
                "in": "path",
                "name": "author_id",
                "description": "Id of the author who posted post post_id",
                "required": "true",
            },
        ],
        "responses": {
            200: {"description": "A list of likes", "schema": likes_schema},
            404: {"description": "Author not found"},
        },
    }
)
@basic_auth.required
def get_author_likes(author_id: str):
    """
    List what PUBLIC things AUTHOR_ID liked.

    It’s a list of of likes originating from this author
    """
    # Again author must exist on our server
    author = Author.query.filter_by(id=author_id).first_or_404()

    # Fetching object urls from database
    stmt = author_likes_posts.select().where(author_likes_posts.c.author == author.url)
    result = db.session.execute(stmt)
    post_urls_rows = result.all()
    post_urls = [getattr(row, "post") for row in post_urls_rows]

    stmt = author_likes_comments.select().where(author_likes_comments.c.author == author.url)
    result = db.session.execute(stmt)
    comment_urls_rows = result.all()
    comment_urls = [getattr(row, "comment") for row in comment_urls_rows]

    # Generating objects
    likes = []
    for url in post_urls + comment_urls:
        like = {"type": "like", "author": author.getJSON(), "object": url}

        likes.append(like)

    return {"type": "likes", "items": likes}, 200


@posts_bp.route("/<string:author_id>/inbox", methods=["GET"])
@login_required
def get_inbox(author_id: str):
    """if authenticated get a list of posts sent to AUTHOR_ID (paginated)"""

    author = Author.query.filter_by(id=author_id).first_or_404()

    posts = (
        Post.query.filter_by(Post.author != author.url, inbox=author_id)
        .order_by(desc(Post.published))
        .paginate(**get_pagination_params().dict)
        .items
    )

    return {"type": "posts", "items": [post.getJSON() for post in posts]}, 200


@posts_bp.route("/<string:author_id>/inbox/", methods=["POST"])
@swag_from(
    {
        "tags": ["Posts", "Likes", "Comments", "Follow request", "Inbox"],
        "description": "Send a like, comment, follow or post to the author's inbox having id as author_id",
        "paramters": [
            {"in": "path", "name": "author_id", "required": "true", "description": "Id of the recepient author"},
            {
                "in": "body",
                "required": "true",
                "schema": {"oneOf": [post_schema, like_schema, comment_schema, follow_schema]},
            },
        ],
        "responses": {
            201: {
                "description": "Post/follow/like/comment sent to inbox successfully",
                "schema": {"properties": {"message": {"type": "string", "example": "Post created successfully"}}},
            },
            400: {
                "description": "Request body contains invalid data.",
                "schema": {"properties": {"message": {"type": "string", "example": "Invalid data"}}},
            },
        },
    }
)
@basic_auth.required
def post_inbox(author_id: str):
    """
    Sends the post/like/follow/comment to the inbox of the author with author_id
    """
    # TODO check if 400 is thrown after data validation

    data = request.json
    type = data["type"].lower()
    response = {}
    match type:
        case "post":
            response = make_post(data, author_id)
        case "like":
            response = make_like(data, author_id)
        case "follow":
            response = make_follow(data, author_id)
        case "comment":
            response = make_comment(data, author_id)
    return response


@posts_bp.route("/<string:author_id>/inbox", methods=["DELETE"])
@login_required
def clear_inbox(author_id: str):
    """clear the inbox"""
    post = Post.query.filter_by(inbox=author_id).first_or_404()

    db.session.delete(post)
    db.session.commit()

    return {"success": 1, "message": "Inbox cleared succesfully"}, 200


def make_post(data, author_id, post_id=None):
    """
    Combined function to make new post using HTTP POST and PUT.
    The author makes these api calls.
    """
    visibility = data.get("visibility")
    if visibility == "PUBLIC":
        visibility = Visibility.PUBLIC
    elif visibility == "FRIENDS":
        visibility = Visibility.FRIENDS

    if post_id:
        post = Post(
            id=post_id,
            published=data.get("published"),
            title=data.get("title"),
            origin=data.get("origin"),
            source=data.get("source"),
            description=data.get("description"),
            content=data.get("content"),
            contentType=data.get("contentType"),
            categories=",".join(data.get("categories")),
            visibility=visibility,
            unlisted=data.get("unlisted"),
            author=data.get("author").get("id"),
            inbox=author_id,
        )
    else:
        post = Post(
            published=data.get("published"),
            title=data.get("title"),
            origin=data.get("origin"),
            source=data.get("source"),
            description=data.get("description"),
            content=data.get("content"),
            contentType=data.get("contentType"),
            categories=",".join(data.get("categories")),
            visibility=data.get("visibility"),
            unlisted=data.get("unlisted"),
            author=data.get("author").get("id"),
            inbox=author_id,
        )
    db.session.add(post)
    db.session.commit()

    return {"message": "Post created successfully."}, 201


def make_like(json, author_id):
    # Author's inbox must exist on server
    Author.query.filter_by(id=author_id).first_or_404()

    data = request.json
    object_id = data.get("object")
    type = get_object_type(object_id)
    made_by = data.get("author").get("id")
    response = {}
    try:
        match type:
            case "comment":
                stmt = author_likes_comments.insert().values(author=made_by, comment=object_id)
                db.session.execute(stmt)
                db.session.commit()
                response = {"success": 1, "message": "Like created"}, 201
            case "post":
                stmt = author_likes_posts.insert().values(author=made_by, post=object_id)
                db.session.execute(stmt)
                db.session.commit()
                response = {"success": 1, "message": "Like created"}, 201
            case None:
                response = {"success": 0, "message": "Like not created"}, 404
    except IntegrityError:
        response = {"success": 0, "message": "Already liked"}
    return response


def make_follow(json, author_id):
    pass


def make_comment(json, author_id):
    """
    Submit a comment made on author's post with id as author_id.
    Arguments:
        author_id: ID of the author who made the
    """
    comment_id = json.get("id")
    # TODO might need a better way
    post_url = comment_id[: comment_id.index("comments") - 1]
    comment = Comment(
        created=json.get("published"),
        content=json.get("comment"),
        contentType=json.get("contentType"),
        id=comment_id,
        author_id=json.get("author").get("id"),
        post_url=post_url,
    )
    db.session.add(comment)
    db.session.commit()

    return {"message": "Comment made succesfully."}, 201
