import base64
import logging
from dataclasses import asdict
from urllib.parse import urlparse

import requests
from flasgger import swag_from
from flask import Blueprint, jsonify, request
from flask_login import login_required
from sqlalchemy import and_, desc
from sqlalchemy.exc import IntegrityError

from api import basic_auth, db
from api.user.author.model import Author, NonLocalAuthor
from api.user.comments.model import Comment
from api.user.followers.model import LocalFollower, NonLocalFollower
from api.user.posts.docs import *
from api.user.posts.model import Post, inbox_table
from api.user.relations import author_likes_comments, author_likes_posts
from api.utils import Visibility, generate_object_ID, get_author_info, get_object_type, get_pagination_params

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
    """Get the public post whose id is post_id from author with id author_id"""
    author = Author.query.filter_by(id=author_id).first_or_404()
    post_search = Post.query.filter_by(id=post_id, author=author.id).first_or_404()

    return post_search.getJSON(), 200


@posts_bp.route("/<string:author_id>/posts/<string:post_id>", methods=["POST"])
@login_required
def edit_post(author_id: str, post_id: str):
    """
    Update the post whose id is POST_ID (must be authenticated) ie the person
    editing the post must be the author of the post.
    json received must have all columns to be updated as key value pairs
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
@login_required
def delete_post(author_id: str, post_id: str):
    """remove the post whose id is post_id"""
    # todo author can remove post from it's own inbox this will be achieved
    #  by authenticating that logged in user is author itself
    author = Author.query.filter_by(id=author_id).first_or_404()
    post = Post.query.filter_by(id=post_id, author=author.id).first_or_404()

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
@login_required
def create_post_auto_gen_id(author_id: str):
    """
    Create a new post but generate a new id.
    Arguments:
        author_id: object id of the local/remote author who made or re-shared the post.

    The author id/url in the json body is author
    """
    # todo put this in a function repeated code
    post = make_post_local(request.json, author_id)
    if post is None:
        return {"message": "Failed to create post"}, 400

    # todo: eh error handling remains
    fanout_to_local_inbox(post, author_id)

    return {"message": "Successfully created new post"}, 201


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
        Post.query.filter_by(author=author_id, visibility=Visibility.PUBLIC)
        .order_by(desc(Post.published))
        .paginate(**get_pagination_params().dict)
        .items
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
        return "Not found", 404

    decoded_img = base64.b64decode(post.content)
    json = post.getJSON()
    json["content"] = decoded_img

    return json


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
@basic_auth.required
def get_comment_likes(author_id: str, post_id: str, comment_id: str):
    # Author, post must exist on our server otherwise invalid request
    author = Author.query.filter_by(id=author_id).first_or_404()
    post = Post.query.filter_by(author=author.id, id=post_id).first_or_404()

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

        # author = get_author_info(author_url)

        # If the author (remote) has been deleted from there server
        # or does not exist then we skip that like (TODO should we delete such a like)
        if not author:
            continue

        name = author.get("displayName")
        summary = name + "likes your comment." if name else ""
        like = {"type": "like", "author": author.getJSON(), "object": post.url, "summary": summary}

        likes.append(like)

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
    List what PUBLIC things author_id liked.

    It’s a list of of likes originating from this author
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
@login_required
def get_inbox(author_id: str):
    """if authenticated get a list of posts sent to author_id (paginated)"""

    author = Author.query.filter_by(id=author_id).first_or_404()

    posts = (
        Post.query.join(inbox_table)
        .filter(inbox_table.c.meant_for == author_id)
        .order_by(desc(Post.published))
        .paginate(**get_pagination_params().dict)
        .items
    )

    return {"type": "posts", "items": [post.getJSON() for post in posts]}, 200


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
    # todo remaining @matt:
    #   comment

    data = request.json
    post_type = data["type"].lower()
    response = {}
    match post_type:
        case "post":
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
@login_required
def clear_inbox(author_id: str):
    """clear the inbox"""
    #  todo authenticate self
    statement = inbox_table.delete().where(inbox_table.c.meant_for == author_id)
    db.session.execute(statement)
    db.session.commit()

    return {"success": 1, "message": "Inbox cleared succesfully"}, 200


# Note: Some code repetition but imo easier to reason about maybe can refactor later
def make_post_local(data, author_id, post_id=None):
    # verify required fields
    required_fields = [
        "published",
        "title",
        "origin",
        "source",
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
    try:
        post = Post(
            id=post_id,
            url=f"http://{request.headers['Host']}/{meant_for.id}/posts/{post_id}",
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
            author=author.id,
        )
        db.session.add(post)
        db.session.commit()
    except Exception as e:
        logger.exception("failed to create post local: ")
        return None

    return post


def make_post_non_local(data, author_id):
    """
    Combined function to make new post using HTTP POST and PUT.
    The author makes these api calls.
    """
    if not data.get("author", None) or not data.get("author").get("id", None):
        return {"message": "Missing Author"}, 400

    if data.get("id") is None:
        return {"message": "Missing Post ID"}, 400

    post_id = data.get("id")

    meant_for = Author.query.filter_by(id=author_id).first()
    if meant_for is None:
        return {"message": "Author doesn't exist"}, 404

    visibility = data.get("visibility")
    if visibility == "PUBLIC":
        visibility = Visibility.PUBLIC
    elif visibility == "FRIENDS":
        visibility = Visibility.FRIENDS

    # verification of all the fields needed
    author = data.get("author")
    required_fields = ["id", "host", "displayName", "url", "github", "profileImage"]
    for field in required_fields:
        if author.get(field, None) is None:
            return {"message": "Author with incomplete fields"}, 400

    if Author.query.filter_by(id=data.get("author").get("id")).first() is not None:
        return {"message": "Local authors shouldn't send to inbox directly"}, 400

    author = NonLocalAuthor.query.filter_by(id=data.get("author").get("id")).first()

    if not author:
        author = create_non_local_author(data.get("author"))

    if not author:
        return {"message": "Missing fields in author"}, 400

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
        author=author.id,
    )
    db.session.add(post)
    statement = inbox_table.insert().values(post_id=post_id, meant_for=author_id)
    db.session.execute(statement)
    db.session.commit()

    return {"message": "Post created successfully."}, 201


def fanout_to_local_inbox(post: Post, author: str = None):
    if post.visibility == Visibility.PUBLIC:
        authors = Author.query.all()
        to_insert = []
        for author in authors:
            to_insert.append({"post_id": post.id, "meant_for": author.id})
        statement = inbox_table.insert().values(to_insert)
        db.session.execute(statement)
        db.session.commit()
    if post.visibility == Visibility.FRIENDS:
        # todo: eh need a method to determine friends
        pass


def fanout_to_foreign_inbox(post, author_id):
    author_url = f"http://{request.headers['Host']}/authors/{author_id}"
    all_foreign = NonLocalFollower.query.filter_by(followed_url=author_url).all()
    logger.debug(f"logging to {len(all_foreign)} endpoints")
    post_to_send = post.getJSON()
    for foreign in all_foreign:
        # author ids are URLs that we should be able to just tack on /inbox to
        # we strip the trailing slash to make sure we're not double adding one in case one already exists
        foreign_inbox_url = foreign.follower_url.rstrip("/") + "/inbox"
        try:
            resp = requests.post(
                foreign_inbox_url, data={"type": "inbox", "author": author_url, "items": [post_to_send]}
            )
            logger.debug(f"received response for ...{foreign_inbox_url}: {resp.status_code}")
            if 200 >= resp.status_code > 300:
                # breakpoint()
                logger.warning("non-300 status code!!!")
        except:
            logger.exception("failed to send to foreign author: ")


def make_like(json, author_id):
    # Author's inbox must exist on server
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
        return {"message": "Missing fields in author"}, 400

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
    if not (followed_object := json.get("object")):
        return {"success": 0, "message": "object key must be specified for inbox!"}, 400

    assert json["type"].lower() == "follow"
    actor = json["actor"]

    # we need to parse the object id to see who it's coming from :\
    parsed = urlparse(actor["url"])
    # hardcode kekw
    if parsed.hostname.startswith("bigger-yoshi"):
        FollowTable = LocalFollower
    else:
        FollowTable = NonLocalFollower

    logger.info(f"parsed hostname from f{actor['url']}: {parsed.hostname} -> querying {FollowTable.__name__}")

    if FollowTable == NonLocalFollower:
        non_local_exists = NonLocalAuthor.query.filter_by(url=actor["url"]).first()
        if non_local_exists:
            logger.info("foreign author already exists, declining to update them for now (todo: fix?)")
        else:
            logger.info("new foreign author encountered, let's keep record of them")
            create_non_local_author(actor)

    if FollowTable.query.filter_by(follower_url=actor["url"], followed_url=author_id):
        return {"success": 0, "message": f"A follow request is already pending for {author_id=}!"}

    db.session.add(FollowTable(follower_url=actor["url"], followed_url=author_id, approved=False))
    db.session.commit()
    return {"success": 1, "message": "Follow request has been sent!"}


# todo fix later too tired right now
def make_comment(json, author_id):
    """
    Submit a comment made on author's post with id as author_id.
    Arguments:
        author_id: ID of the author who made the
    """

    comment_id = json.get("id") + generate_object_ID()
    author_id = json.get("author", {}).get("id")
    if comment_id is None or author_id is None:
        return {"message": "Missing fields"}, 400

    author = Author.query.filter_by(id=author_id.split("/")[-1]).first()
    if author is None:
        author = NonLocalAuthor.query.filter_by(id=author_id).first()

    # if author doesn't exist both locally and non-locally
    if author is None:
        author = create_non_local_author(json.get("author"))

    # if failed to create the author
    if author is None:
        return {"message": "Missing fields in author"}, 400

    # TODO might need a better way
    post_id = comment_id.split("posts")[1].split("/")[1]
    comment = Comment(
        published=json.get("published"),
        comment=json.get("comment"),
        contentType=json.get("contentType"),
        author_id=author.id,
        id=comment_id,
        post_id=post_id,
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
            displayName=author_to_add["displayName"],
            github=author_to_add["github"],
            profileImage=author_to_add["profileImage"],
        )
        db.session.add(author)
        db.session.commit()
        return author
    except Exception:
        return None
