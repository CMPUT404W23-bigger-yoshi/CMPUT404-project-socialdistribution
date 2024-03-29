import base64
import logging
from dataclasses import asdict
from datetime import datetime
from io import BytesIO
from urllib.parse import urlparse

import requests
from flasgger import swag_from
from flask import Blueprint, Response, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy import and_, desc
from sqlalchemy.exc import IntegrityError

from api import API_HOSTNAME, basic_auth, db
from api.admin.utils import auth_header_for_url
from api.user.author.model import Author, NonLocalAuthor
from api.user.comments.model import Comment
from api.user.followers.model import LocalFollower, NonLocalFollower
from api.user.posts.docs import *
from api.user.posts.model import Post, inbox_table
from api.user.relations import author_likes_comments, author_likes_posts
from api.utils import Approval, Visibility, generate_object_ID, get_author_info, get_object_type, get_pagination_params

# note: this blueprint is usually mounted under  URL prefix
posts_bp = Blueprint("posts", __name__)

logger = logging.getLogger(__name__)


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
    """Get the public post whose id is post_id from author with id author_id."""
    author = Author.query.filter_by(id=author_id).first_or_404()
    post_search = Post.query.filter_by(id=post_id, author=author.id).first_or_404()

    return post_search.getJSON(), 200


@posts_bp.route("/<string:author_id>/posts/<string:post_id>", methods=["POST"])
@swag_from(
    {
        "tags": ["Posts"],
        "description": "Update the post with id post_id authored by author_id. The authenticated user must be the author of the post.",
        "parameters": [
            {"in": "path", "name": "author_id", "description": "Id of the author of the post"},
            {"in": "path", "name": "post_id", "description": "Id of the post to update"},
        ],
        "requestBody": {
            "description": "JSON object containing columns to be updated as key-value pairs",
            "required": True,
        },
        "responses": {
            201: {"description": "Post edited successfully.", "schema": post_schema},
            400: {
                "description": "Cannot update post id after post has been created, or cannot update author after post has been created."
            },
            404: {"description": "Author not found or Post not found"},
        },
    }
)
@login_required
def edit_post(author_id: str, post_id: str):
    """
    Update the post with id post_id authored by author_id. The authenticated user must be the author of the post.
    """
    # TODO handle authentication
    data = request.json

    # Modify json to be compatible with model here (if required)
    # todo author can edit posts written by themselves?

    author = Author.query.filter_by(id=author_id).first_or_404()
    post = Post.query.filter_by(id=post_id, author=author.id).first_or_404()

    if data.get("id", None) is not None and data.get("id").split("/")[-1] != post.id:
        return {"success": 0, "message": "Cannot update post id after post has been created"}, 400

    if data.get("author", {}).get("id", None) is not None and data["author"]["id"] != post.author:
        return {"success": 0, "message": "Cannot update author after post has been created"}, 400

    for k, v in data.items():
        if k == "author":
            continue
        if k == "categories":
            v = ",".join(v)
        if k == "visibility":
            if v == "PUBLIC":
                v = Visibility.PUBLIC
            if v == "FRIENDS":
                v = Visibility.FRIENDS
        setattr(post, k, v)

    db.session.commit()

    return {"success": 1, "message": "Post edited successfully."}, 201


@posts_bp.route("/<string:author_id>/posts/<string:post_id>", methods=["DELETE"])
@swag_from(
    {
        "tags": ["Posts"],
        "description": "Remove the post with id post_id authored by author_id. The authenticated user must be the author of the post.",
        "parameters": [
            {"in": "path", "name": "author_id", "description": "Id of the author of the post"},
            {"in": "path", "name": "post_id", "description": "Id of the post to delete"},
        ],
        "responses": {
            200: {"description": "Post deleted successfully."},
            404: {"description": "Author not found or Post not found"},
        },
    }
)
@login_required
def delete_post(author_id: str, post_id: str):
    """
    Remove the post with id post_id authored by author_id. The authenticated user must be the author of the post.
    """
    # todo author can remove post from it's own inbox this will be achieved
    #  by authenticating that logged in user is author itself
    author = Author.query.filter_by(id=author_id).first_or_404()
    post = Post.query.filter_by(id=post_id, author=author.id).first_or_404()

    db.session.delete(post)
    db.session.commit()
    return {"success": 1, "message": "Post deleted successfully."}, 200


@posts_bp.route("/<string:author_id>/posts/<string:post_id>", methods=["PUT"])
@swag_from(
    {
        "tags": ["Posts"],
        "description": "Create a new post with id post_id authored by author_id.",
        "parameters": [
            {"in": "path", "name": "author_id", "description": "Id of the author of the post"},
            {"in": "path", "name": "post_id", "description": "Id of the new post to create"},
        ],
        "requestBody": {
            "description": "JSON object containing the properties of the new post",
            "required": True,
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/PostSchema"}}},
        },
        "responses": {
            201: {"description": "Successfully created new post", "schema": post_schema},
            400: {"description": "Failed to create post"},
        },
    }
)
@login_required
def create_post(author_id: str, post_id: str):
    """
    Create a new post with id post_id authored by author_id.
    """
    post = make_post_local(request.json, author_id, post_id)
    if post is None:
        return {"message": "Failed to create post"}, 400

    # todo :
    #  * error handling
    #  * foreign authors inbox
    fanout_to_local_inbox(post, author_id)
    fanout_to_foreign_inbox(post, author_id)

    return {"message": "Successfully created new post"}, 201


@posts_bp.route("/<string:author_id>/posts/", methods=["POST"])
@swag_from(
    {
        "tags": ["Posts"],
        "description": "Creates a new post with a generated ID.",
        "parameters": [
            {"in": "path", "name": "author_id", "description": "ID of the author of the post."},
        ],
        "responses": {
            201: {"description": "Post created successfully.", "schema": post_schema},
            400: {"description": "Failed to create post."},
        },
    }
)
@login_required
def create_post_auto_gen_id(author_id: str):
    """
    Create a new post but generate a new id.
    """
    # todo put this in a function repeated code
    post = make_post_local(request.json, author_id)
    if post is None:
        return {"message": "Failed to create post"}, 400

    # todo: eh error handling remains
    fanout_to_local_inbox(post, author_id)
    fanout_to_foreign_inbox(post, author_id)

    return {"message": "Successfully created new post", "post": post.getJSON()}, 201


@posts_bp.route("/<string:author_id>/posts", methods=["GET"])
@posts_bp.route("/<string:author_id>/posts/", methods=["GET"])
@swag_from(
    {
        "tags": ["Posts"],
        "description": "Returns a recent public posts authored by author_id.",
        "parameters": [
            {"in": "path", "name": "author_id", "description": "Id of the author of the posts"},
            {
                "in": "query",
                "name": "page",
                "description": "Page number for the resulting list of public posts",
                "type": "integer",
            },
            {"in": "query", "name": "size", "description": "Number of items per page", "type": "integer"},
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
    """
    author = Author.query.filter_by(id=author_id).first_or_404()
    posts = (
        Post.query.filter_by(author=author_id, visibility=Visibility.PUBLIC, unlisted=False)
        .order_by(desc(Post.published))
        .paginate(**get_pagination_params().dict)
        .items
    )

    if current_user.is_authenticated and current_user.id == author_id:
        posts.extend(
            Post.query.filter_by(unlisted=False, visibility=Visibility.PRIVATE, author=author_id)
            .order_by(desc(Post.published))
            .all()
        )

    return {"type": "posts", "items": [post.getJSON() for post in posts]}, 200


# todo check @matt
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
            404: {"description": "Not an Image"},
        },
    }
)
@basic_auth.required
def post_as_base64_img(author_id: str, post_id: str):
    """
    Get the public post converted to binary as an image
    """
    author = Author.query.filter_by(id=author_id).first_or_404()
    post = Post.query.filter_by(author=author_id, id=post_id).first_or_404()
    if not (post.contentType == "application/base64" or post.contentType.startswith("image/")):
        return "Not an image", 404

    # remove the header from the string
    data = post.content.split(",")[1]

    # decode the base64 string
    decoded = base64.b64decode(data)

    # create a BytesIO object from the decoded bytes
    img_io = BytesIO(decoded)

    # return the byte stream as a response with the appropriate headers
    return Response(img_io.getvalue(), mimetype=post.contentType)


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
            404: {"description": "Author or post not foundauthor=author.id, "},
        },
    }
)
@basic_auth.required
def get_likes(author_id: str, post_id: str):
    """Get a list of likes from other authors on author_id’s post post_id"""
    # Author, post must exist on our server otherwise invalid request
    author = Author.query.filter_by(id=author_id).first_or_404()
    post = Post.query.filter_by(id=post_id).first_or_404()

    # fetch all author urls who like this post from database
    stmt = author_likes_posts.select().where(author_likes_posts.c.post == post.id)
    result = db.session.execute(stmt)
    authors = result.all()
    authors = [getattr(row, "author") for row in authors]

    # Generating likes
    likes = []
    for author_id in authors:
        author = Author.query.filter_by(id=author_id).first()
        if author is None:
            author = NonLocalAuthor.query.filter_by(id=author_id).first()

        # If the author (remote) has been deleted from there server
        # or does not exist then we skip that like (TODO should we delete such a like)
        if not author:
            continue

        name = author.username
        summary = name + "likes your post." if name else ""
        like = {"type": "like", "author": author.getJSON(), "object": post.url, "summary": summary}

        likes.append(like)

    return {"type": "likes", "items": likes}


@posts_bp.route("/<string:author_id>/posts/<string:post_id>/comments/<string:comment_id>/likes", methods=["GET"])
@swag_from(
    {
        "tags": ["Likes"],
        "description": "Get likes on the comment with comment_id, for post with post_id written by the author with author_id.",
        "parameters": [
            {"in": "path", "name": "author_id", "description": "Id of the author of the post"},
            {"in": "path", "name": "post_id", "description": "Id of the post containing the comment"},
            {"in": "path", "name": "comment_id", "description": "Id of the comment to get likes for"},
        ],
        "responses": {
            200: {"description": "Likes fetched successfully", "schema": likes_schema},
            401: {"description": "Unauthorized access"},
            404: {"description": "Author, post or comment not found on our server"},
        },
    }
)
@basic_auth.required
def get_comment_likes(author_id: str, post_id: str, comment_id: str):
    """
    Get likes on the comment with comment_id for the post with post_id written by the author with author_id.
    """
    # Author, post must exist on our server otherwise invalid request
    comment = Comment.query.filter_by(id=comment_id).first_or_404()

    # fetch all author urls who like this comment from database
    authors_that_like_comment = db.session.execute(
        author_likes_comments.select().where(author_likes_comments.c.comment == comment.id)
    ).all()
    authors_that_like_comment = [getattr(row, "author") for row in authors_that_like_comment]

    # Generating likes
    likes = []
    for author_id in authors_that_like_comment:
        author = Author.query.filter_by(id=author_id).first()
        if author is None:
            author = NonLocalAuthor.query.filter_by(id=author_id).first()

        # author = get_author_info(author_url)

        # If the author (remote) has been deleted from their server, we'll probably never know
        # or does not exist then we skip that like (TODO should we delete such a like)
        if not author:
            continue

        summary = f"{author.username} likes your comment."
        likes.append(
            {
                "type": "like",
                "author": author.getJSON(),
                "object": comment.post.url + "/comments/" + comment.id,
                "summary": summary,
            }
        )

    return {"type": "likes", "items": likes}


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
    Returns a list of objects liked by author with author_id
    """
    # Again author must exist on our server
    author = Author.query.filter_by(id=author_id).first_or_404()

    # Fetching object urls from database
    stmt = author_likes_posts.select().where(author_likes_posts.c.author == author.id)
    result = db.session.execute(stmt)
    post_urls_rows = result.all()
    post_urls = [getattr(row, "post") for row in post_urls_rows]

    stmt = author_likes_comments.select().where(author_likes_comments.c.author == author.id)
    result = db.session.execute(stmt)
    comment_urls_rows = result.all()
    comment_urls = [getattr(row, "comment") for row in comment_urls_rows]

    # Generating objects
    likes = []
    for url in post_urls + comment_urls:
        like = {"type": "like", "author": author.getJSON(), "object": url}
        likes.append(like)

    return {"type": "liked", "items": likes}


@posts_bp.route("/<string:author_id>/inbox", methods=["GET"])
@swag_from(
    {
        "tags": ["Inbox"],
        "description": "Get a list of posts sent to a specific author (paginated).",
        "parameters": [
            {"in": "path", "name": "author_id", "required": "true", "description": "author_id of author."},
        ],
        "responses": {
            200: {"description": "List of posts sent to the author successfully retrieved.", "schema": inbox_schema},
            404: {"description": "Author with the given author_id is not found."},
        },
    }
)
@login_required
def get_inbox(author_id: str):
    """Get a list of posts sent to author_id (paginated)."""

    author = Author.query.filter_by(id=author_id).first_or_404()

    posts = (
        Post.query.filter(Post.unlisted == False)
        .join(inbox_table)
        .filter(inbox_table.c.meant_for == author_id)
        .order_by(desc(Post.published))
        .paginate(**get_pagination_params().dict)
        .items
    )

    return {"type": "posts", "items": [post.getJSON() for post in posts]}, 200


@login_required
def get_inbox(author_id: str):
    """if authenticated get a list of posts sent to author_id (paginated)"""

    author = Author.query.filter_by(id=author_id).first_or_404()

    posts = (
        Post.query.filter(Post.unlisted == False)
        .join(inbox_table)
        .filter(inbox_table.c.meant_for == author_id)
        .order_by(desc(Post.published))
        .paginate(**get_pagination_params().dict)
        .items
    )

    return {"type": "posts", "items": [post.getJSON() for post in posts]}, 200


@posts_bp.route("/foreign-inbox/<path:author_url>/", methods=["POST"])
@swag_from(
    {
        "tags": ["Posts", "Likes", "Comments", "Follow request", "Inbox"],
        "description": "Send a like, comment, follow or post to a foreign author's inbox having id as author_id",
        "parameters": [
            {"in": "path", "name": "author_id", "required": "true", "description": "Id of the recepient author"},
            {
                "in": "body",
                "required": "true",
                "schema": inbox_schema,  # {"oneOf": [post_schema, like_schema, comment_schema, follow_schema]},
                "description": "Object to be sent to inbox",
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
def post_foreign_inbox(author_url: str):
    """
    Send a post/like/follow/comment to a foreign author's inbox having id as author_id.
    """
    # assumption: author_id  will be a fully qualified URL
    parsed = urlparse(author_url)

    if not all([parsed.scheme, parsed.netloc]):
        logger.error("you are calling the wrong inbox endpoint. This one expects a fully qualified URL in all cases :/")
        return {"message": "You gave use a shit author url dawg", "success": 0}

    logger.info(
        f"special route: proxying request from foreign-inbox to {author_url}" f" with auth credentials along the way"
    )
    logger.info(f"Proxying your request with data: {request.json}\nWith credentials: {auth_header_for_url(author_url)}")
    res = requests.post(author_url, headers=auth_header_for_url(author_url), json=request.json)
    # note (matt): I didn't come up with this,
    # these guys did: https://stackoverflow.com/questions/6656363/proxying-to-another-web-service-with-flask
    # We exclude all "hop-by-hop headers" defined by RFC 2616 section 13.5.1 ref.
    # https://www.rfc-editor.org/rfc/rfc2616#section-13.5.1
    excluded_headers = {"content-encoding", "content-length", "transfer-encoding", "connection"}
    headers = {(k, v) for k, v in res.raw.headers.items() if k.lower() not in excluded_headers}

    return Response(res.content, res.status_code, headers)


@posts_bp.route("/foreign-inbox/<path:author_url>/", methods=["GET"])
@swag_from(
    {
        "tags": ["Posts", "Likes", "Comments", "Follow request", "Inbox"],
        "description": "Retrieve messages from a foreign author's inbox with author_url",
        "parameters": [
            {
                "in": "path",
                "name": "author_url",
                "required": "true",
                "description": "URL of the recipient author's inbox",
            },
        ],
        "responses": {
            200: {
                "description": "Messages retrieved successfully",
                "schema": {"type": "object", "properties": {"messages": {"type": "array", "items": inbox_schema}}},
            },
            400: {
                "description": "Request contains invalid data.",
                "schema": {"properties": {"message": {"type": "string", "example": "Invalid data"}}},
            },
        },
    }
)
@basic_auth.required
def get_foreign_inbox(author_url: str):
    """
    Retrieve messages from a foreign author's inbox with author_url
    """
    # assumption: author_id  will be a fully qualified URL
    parsed = urlparse(author_url)
    if not all([parsed.scheme, parsed.netloc]):
        logger.error("you are calling the wrong inbox endpoint. This one expects a fully qualified URL in all cases :/")
        return {"message": "You gave use a shit author url dawg", "success": 0}

    logger.info(
        f"special route: proxying request from foreign-inbox to {author_url}" f" with auth credentials along the way"
    )

    res = requests.get(author_url, headers=auth_header_for_url(author_url))
    # note (matt): I didn't come up with this,
    # these guys did: https://stackoverflow.com/questions/6656363/proxying-to-another-web-service-with-flask
    # We exclude all "hop-by-hop headers" defined by RFC 2616 section 13.5.1 ref.
    # https://www.rfc-editor.org/rfc/rfc2616#section-13.5.1
    excluded_headers = {"content-encoding", "content-length", "transfer-encoding", "connection"}
    headers = {(k, v) for k, v in res.raw.headers.items() if k.lower() not in excluded_headers}
    return Response(res.content, res.status_code, headers)


# todo check
@posts_bp.route("/<string:author_id>/inbox/", methods=["POST"])
@swag_from(
    {
        "tags": ["Posts", "Likes", "Comments", "Follow request", "Inbox"],
        "description": "Send a like, comment, follow or post to the author's inbox having id as author_id",
        "parameters": [
            {"in": "path", "name": "author_id", "required": "true", "description": "Id of the recepient author"},
            {
                "in": "body",
                "required": "true",
                "schema": inbox_schema,  # {"oneOf": [post_schema, like_schema, comment_schema, follow_schema]},
                "description": "Object to be sent to inbox",
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
    logger.info(f"Received request in inbox data: {request.json}")
    data = request.json
    post_type = data["type"].lower()
    response = {}
    match post_type:
        case "post":
            author_obj = data.get("author")

            # if post sent privately to local inbox
            if Author.query.filter_by(id=author_obj.get("id").split("/")[-1]).first() is not None:
                logger.info("Creating a local post")
                post = make_post_local(data, author_id)

                if post is None:
                    logger.info(f"Failed to create a post with data: {data}")
                    response = {"message": "Failed to create a post locally"}, 400
                    return response
                statement = inbox_table.insert().values(post_id=post.id, meant_for=author_id)
                db.session.execute(statement)
                db.session.commit()
                response = {"message": "Successfully created post"}, 201
                return response

            response = make_post_non_local(data, author_id)
        case "like":
            response = make_like(data, author_id)
        case "follow":
            response = make_follow(data, author_id)
        case "comment":
            response = make_comment(data, author_id)
    return response


# todo check
@posts_bp.route("/<string:author_id>/inbox", methods=["DELETE"])
@swag_from(
    {
        "tags": ["Inbox"],
        "summary": "Clear the inbox",
        "parameters": [
            {
                "in": "path",
                "name": "author_id",
                "description": "The ID of the author whose inbox will be cleared",
                "required": "true",
                "schema": {"type": "string"},
            }
        ],
        "responses": {"200": {"description": "Inbox cleared successfully"}, "404": {"description": "Author not found"}},
    }
)
@login_required
def clear_inbox(author_id: str):
    """Clear the inbox for author_id"""
    #  todo authenticate self
    statement = inbox_table.delete().where(inbox_table.c.meant_for == author_id)
    db.session.execute(statement)
    db.session.commit()

    return {"success": 1, "message": "Inbox cleared successfully"}, 200


# Note: Some code repetition but imo easier to reason about maybe can refactor later
def make_post_local(data, author_id, post_id=None):
    # verify required fields
    required_fields = [
        "published",
        "title",
        "description",
        "content",
        "contentType",
        "categories",
        "visibility",
        "unlisted",
        "author",
    ]
    for field in required_fields:
        if data.get(field, None) is None:
            logger.info(f"posted to {author_id=}, but didn't specify required field {field}. aborting")
            return None

    if data.get("author").get("id", None) is None:
        logger.info(f"posted to {author_id=}, but didn't specify ID in the body")
        return None

    author = Author.query.filter_by(id=data["author"]["id"].split("/")[-1]).first()
    if author is None:
        logger.info(f"{author_id=} does not exist")
        return None

    meant_for = Author.query.filter_by(id=author_id).first()
    if meant_for is None:
        return None

    post_id = post_id if post_id is not None else generate_object_ID()

    # todo write a to_str
    visibility = data.get("visibility")
    if visibility == "PUBLIC":
        visibility = Visibility.PUBLIC
    elif visibility == "FRIENDS":
        visibility = Visibility.FRIENDS
    elif visibility == "PRIVATE":
        visibility = Visibility.PRIVATE
    try:
        post = Post(
            id=post_id,
            published=data.get("published"),
            title=data.get("title"),
            description=data.get("description"),
            content=data.get("content"),
            contentType=data.get("contentType"),
            categories=",".join(data.get("categories", [])),
            visibility=visibility,
            unlisted=data.get("unlisted"),
            author=author.id,
        )
        db.session.add(post)
        db.session.commit()
    except Exception as e:
        logger.exception("failed to create post local:")
        return None

    return post


def make_post_non_local(data, author_id):
    """
    Combined function to make new post using HTTP POST and PUT.
    The author makes these api calls.
    """
    logger.info(f"Trying to create non local post with data: {data}\nFor Author: {author_id}")
    author_obj = data.get("author")
    if not data.get("author", None) or not author_obj.get("id", None):
        logger.info("Missing Author")
        return {"message": "Missing Author"}, 400

    if data.get("id") is None:
        logger.info("Missing Post Id")
        return {"message": "Missing Post ID"}, 400

    post_id = data.get("id")

    meant_for = Author.query.filter_by(id=author_id).first()
    if meant_for is None:
        logger.info("Author doesn't exist")
        return {"message": "Author doesn't exist"}, 404

    visibility = data.get("visibility")
    if visibility == "PUBLIC":
        visibility = Visibility.PUBLIC
    elif visibility == "FRIENDS":
        visibility = Visibility.FRIENDS
    elif visibility == "PRIVATE":
        visibility = Visibility.PRIVATE

    # verification of all the fields needed
    author_obj = data.get("author")
    if not author_obj:
        logger.info("Failed to find author obj in request")
        return {"message": "failed to find author obj in request", "success": 0}, 400

    required_fields = ["id", "host", "displayName", "url", "profileImage"]
    for field in required_fields:
        if author_obj.get(field, None) is None:
            logging.info(f"Author is missing field: {field}")
            return {"message": "Author with incomplete fields"}, 400

    if Author.query.filter_by(id=author_obj.get("id")).first() is not None:
        logger.info("Local author shouldn't send info to inbox directly")
        return {"message": "Local authors shouldn't send to inbox directly"}, 400

    author = NonLocalAuthor.query.filter_by(id=author_obj.get("id")).first()

    if not author:
        logger.info("Creating record of previous non-existent author: ")
        author = create_non_local_author(author_obj)

    post = Post(
        id=post_id,
        published=data.get("published"),
        url=post_id,
        title=data.get("title"),
        origin=data.get("origin"),
        source=data.get("source"),
        description=data.get("description"),
        content=data.get("content"),
        contentType=data.get("contentType"),
        categories=",".join(data.get("categories", [])),
        visibility=visibility,
        unlisted=data.get("unlisted"),
        author=author.id,
    )
    db.session.add(post)
    # this commit is necessary to satisfy FK constraints with postgres, even in this order for some reason. weird
    db.session.commit()
    statement = inbox_table.insert().values(post_id=post_id, meant_for=author_id)
    db.session.execute(statement)
    db.session.commit()

    return {"message": "Post created successfully."}, 201


def fanout_to_local_inbox(post: Post, author_id) -> None:
    if post.visibility == Visibility.PUBLIC:
        authors = Author.query.all()
        to_insert = []
        for author in authors:
            to_insert.append({"post_id": post.id, "meant_for": author.id})
        statement = inbox_table.insert().values(to_insert)
    elif post.visibility == Visibility.FRIENDS:
        author = Author.query.filter_by(id=author_id).first()
        if author is None:  # can't do 404, fan-out shouldn't affect the post creation
            return

        followed_by_author = LocalFollower.query.filter_by(follower_url=author.url, approved=True).all()
        followed_by_author_urls = set(map(lambda x: x.followed_url, followed_by_author))

        follower_of_author = LocalFollower.query.filter_by(followed_url=author.url, approved=True).all()
        follower_of_author_urls = set(map(lambda x: x.follower_url, follower_of_author))

        to_insert = []
        for url in followed_by_author_urls.intersection(follower_of_author_urls):
            friend = Author.query.filter_by(url=url).first()
            to_insert.append({"post_id": post.id, "meant_for": friend.id})

        statement = inbox_table.insert().values(to_insert)
    elif post.visibility == Visibility.PRIVATE:
        return
    else:
        raise ValueError(f"Invalid visibility: {post.visibility}")

    db.session.execute(statement)
    db.session.commit()


def fanout_to_foreign_inbox(post: Post, author_id: str) -> None:
    post_author = Author.query.filter_by(id=author_id).first()
    logger.info(f"finding foreign authors for {post_author} with {post.visibility=}")
    foreign_followers = NonLocalFollower.query.filter_by(followed_url=post_author.url).all()

    if post.visibility == Visibility.FRIENDS and len(foreign_followers) > 0:
        # it is very easy to find when they follow us, but more difficult to determine when we follow them,
        # because follow requests can be denied. what we need to do is:
        #  1. record our local -> remote follow requests, with approval pending
        #       - (currently, we simply proxy the foreign inbox endpoint that this would be sent through)
        #  2. set up an endpoint to *confirm* a follow request has been accepted
        #       - what we can do without needing a separate endpoint is following is change state to
        #       accepted when they send us a post for that user
        logger.warning(f"{post.visibility=} not yet implemented for foreign authors :/")

    post_to_send = post.getJSON()
    logger.info(f"logging to {len(foreign_followers)} endpoints")
    for foreign_follower in foreign_followers:
        # author ids are URLs that we should be able to just tack on /inbox to
        # we strip the trailing slash to make sure we're not double adding one in case one already exists
        foreign_inbox_url = foreign_follower.follower_url.rstrip("/") + "/inbox"
        logger.info(f"Auth headers: {auth_header_for_url(foreign_inbox_url)}\nData: {post_to_send}")
        try:
            resp = requests.post(foreign_inbox_url, json=post_to_send, headers=auth_header_for_url(foreign_inbox_url))
            logger.info(f"received response for ...{foreign_inbox_url}: {resp.status_code}\ndata: {resp.json()}")
            if 200 >= resp.status_code > 300:
                # breakpoint()
                logger.warning("non-200 status code!")
        except:
            logger.exception("failed to send to foreign author: ")


def make_like(json, author_id):
    # Author's inbox must exist on server
    logger.debug(f"Like to author: {author_id}")
    Author.query.filter_by(id=author_id).first_or_404()

    data = request.json
    object_id = data.get("object")
    if object_id is None:
        return {"success": 0, "message": "Missing Object"}, 400

    like_type = get_object_type(object_id)
    if like_type not in ["comment", "post"]:
        return {"success": 0, "message": "Invalid Object type"}, 400

    if data.get("author", {}).get("url") is None:
        return {"success": 0, "message": "Missing Author"}, 400

    # todo need a way to distinguish local and foreign authors probably best by host
    made_by = data.get("author").get("id").split("/")[-1]
    author = Author.query.filter_by(id=made_by).first()
    if author is None:
        made_by = data.get("author").get("id")
        author = NonLocalAuthor.query.filter_by(id=made_by).first()

    # if author doesn't exist both locally and non-locally
    if author is None:
        author = create_non_local_author(json.get("author"))
        # if failed to create the author
        if author is None:
            return {"message": "failed to create foreign author"}, 500

    response = {"success": 1, "message": "Like created"}, 201
    try:
        match like_type:
            case "comment":
                stmt = author_likes_comments.insert().values(author=made_by, comment=object_id.split("/")[-1])
                db.session.execute(stmt)
                db.session.commit()
            case "post":
                stmt = author_likes_posts.insert().values(author=made_by, post=object_id.split("/")[-1])
                db.session.execute(stmt)
                db.session.commit()
    except IntegrityError:
        response = {"success": 0, "message": "Already liked"}

    return response


def make_follow(json, author_id):
    logger.info("Received data:", json)
    if not (followed_object := json.get("object")):
        return {"success": 0, "message": "object key must be specified for inbox!"}, 400

    if not (type := json.get("type", None)) or not (actor := json.get("actor", None)):
        return {"success": 0, "message": "Bad follow request"}, 400

    # we need to parse the object id to see who it's coming from :\
    parsed_actor_url = urlparse(actor["url"])
    if parsed_actor_url.hostname == API_HOSTNAME:
        FollowTable = LocalFollower
    else:
        FollowTable = NonLocalFollower

    logger.info(f"parsed hostname from f{actor['url']}: {parsed_actor_url.hostname} -> querying {FollowTable.__name__}")
    if FollowTable == NonLocalFollower:
        non_local_exists = NonLocalAuthor.query.filter_by(url=actor["url"]).first()
        if non_local_exists:
            logger.info("foreign author already exists, declining to update them for now (todo: fix?)")
        else:
            logger.info("new foreign author encountered, let's keep record of them")
            create_non_local_author(actor)

    if FollowTable.query.filter_by(follower_url=actor["url"], followed_url=followed_object["url"]).first():
        return {"success": 0, "message": f"A follow request is already pending for {author_id}!"}, 409

    if actor["url"] == followed_object["url"]:
        return {"success": 0, "message": "Cannot follow yourself"}, 400

    db.session.add(FollowTable(follower_url=actor["url"], followed_url=followed_object["url"], approved=False))
    db.session.commit()
    return {"success": 1, "message": "Follow request has been sent!"}, 201


def make_comment(json, author_id):
    """
    Submit a comment made on author's post with id as author_id.
    Arguments:
        author_id: ID of the author who made the
    """
    logger.info(f"Make comment with content: {json} for author: {author_id}")
    url = json.get("object")
    if not url:
        return {"message": "failed to provide object key"}, 400

    post_exists = Post.query.filter_by(url=url).first()
    if not post_exists:
        return {"message": f"failed to find post @ {url=}"}, 400

    author_id = json.get("author", {}).get("id")
    if author_id is None:
        return {"message": "Missing fields"}, 400

    local_author = Author.query.filter_by(id=author_id.split("/")[-1]).first()
    if local_author is None:
        foreign_author = NonLocalAuthor.query.filter_by(id=author_id).first()
        # if author doesn't exist both locally and non-locally
        if foreign_author is None:
            new_foreign_author = create_non_local_author(json.get("author"))
            # if failed to create the author
            if new_foreign_author is None:
                return {"message": "failed to create author"}, 500
            else:
                author = new_foreign_author
        else:
            author = foreign_author
    else:
        author = local_author

    # TODO might need a better way
    post_url = json["object"]
    comment = Comment(
        published=json.get("published", datetime.now().isoformat()),
        comment=json.get("comment"),
        contentType=json.get("contentType"),
        author_id=author.id,
        post_url=post_url,
    )
    db.session.add(comment)
    db.session.commit()

    return {"message": "Comment made successfully."}, 201


def create_non_local_author(author_to_add):
    try:
        author = NonLocalAuthor(
            id=author_to_add["id"],
            host=author_to_add["host"],
            url=author_to_add["url"],
            username=author_to_add["displayName"],
            github=author_to_add["github"],
            profileImage=author_to_add["profileImage"],
        )
        db.session.add(author)
        db.session.commit()
        return author
    except Exception:
        logger.exception(f"failed to create non-local author: {author_to_add.get('id')}")
        return None


@posts_bp.route("/posts", methods=["GET"])
def get_all_public_posts():
    search = "%{}%".format(API_HOSTNAME)
    posts = Post.query.filter_by(unlisted=False, visibility=Visibility.PUBLIC).order_by(desc(Post.published))
    posts = posts.filter(Post.origin.like(search)).all()
    data = [post.getJSON() for post in posts]
    return {"items": data}
