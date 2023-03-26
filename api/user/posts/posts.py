import base64
from dataclasses import asdict

from flask import Blueprint, jsonify, request
from flask_login import login_required
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError

from api import basic_auth, db
from api.user.author.model import Author, NonLocalAuthor
from api.user.comments.model import Comment
from api.user.posts.model import Post, inbox_table
from api.user.relations import author_likes_comments, author_likes_posts
from api.utils import Visibility, generate_object_ID, get_author_info, get_object_type, get_pagination_params

# note: this blueprint is usually mounted under  URL prefix
posts_bp = Blueprint("posts", __name__)


@posts_bp.route("/<string:author_id>/posts/<string:post_id>", methods=["GET"])
@basic_auth.required
def get_post(author_id: str, post_id: str):
    """get the public post whose id is POST_ID"""
    # author_id in database is complete url
    author = Author.query.filter_by(id=author_id).first_or_404()
    post_search = Post.query.filter_by(id=post_id, author=author.id).first_or_404()

    return post_search.getJSON(), 200


# todo check
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

    if (
        data.get("author", None) is not None
        and data.get("author").get("id", None) is not None
        and data["author"]["id"] != post.author
    ):
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
@basic_auth.required
def post_as_base64_img(author_id: str, post_id: str):
    """
    get the public post converted to binary as an image
     -> return 404 if not an image
    The end point decodes image posts as images. This allows the use of image tags in markdown.
    You can use this to proxy or cache images.
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


# todo check @matt
@posts_bp.route("/<string:author_id>/inbo1x/", methods=["POST"])
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
            response = {"success": 1, "message": "Like created"}, 201
        case "post":
            stmt = author_likes_posts.insert().values(author=made_by, post=object_id)
            db.session.execute(stmt)
            db.session.commit()
            response = {"success": 1, "message": "Like created"}, 201
        case None:
            response = {"success": 0, "message": "Like not created"}, 404

    return response


# todo check @matt
@posts_bp.route("/<string:author_id>/posts/<string:post_id>/likes", methods=["GET"])
@basic_auth.required
def get_likes(author_id: str, post_id: str):
    """a list of likes from other authors on AUTHOR_ID’s post POST_ID"""
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

    return {"type": "likes", "items": likes}


# todo check @matt
@posts_bp.route("/<string:author_id>/liked", methods=["GET"])
@basic_auth.required
def get_author_likes(author_id: str):
    """
    list what PUBLIC things AUTHOR_ID liked.

    It’s a list of of likes originating from this author
    Note: be careful here private information could be disclosed.
    Will need to check if a post is private
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

    return {"type": "likes", "items": likes}


@posts_bp.route("/<string:author_id>/inbox", methods=["GET"])
@login_required
def get_inbox(author_id: str):
    """if authenticated get a list of posts sent to AUTHOR_ID (paginated)"""

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
@basic_auth.required
def post_inbox(author_id: str):
    """
    if the type is “post” then add that post to AUTHOR_ID’s inbox
    if the type is “follow” then add that follow is added to AUTHOR_ID’s inbox to approve later
    if the type is “like” then add that like to AUTHOR_ID’s inbox
    if the type is “comment” then add that comment to AUTHOR_ID’s inbox
    """
    # todo remaining @matt:
    #   post
    #   like
    #   comment
    #   follow

    data = request.json
    type = data["type"].lower()
    response = {}
    match type:
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
            print(f"Data missing Field: {field}")
            return None

    if data.get("author").get("id", None) is None:
        print("Author missing id")
        return None

    author = Author.query.filter_by(id=data["author"]["id"].split("/")[-1]).first()
    if author is None:
        print("Author who wrote this post doesn't exist bad request")
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
        print(e)
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
        # create foreign author
        author = NonLocalAuthor(
            id=author["id"],
            host=author["host"],
            url=author["url"],
            displayName=author["displayName"],
            github=author["github"],
            profileImage=author["profileImage"],
        )
        db.session.add(author)
        db.session.commit()

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
    # todo send to foreign inbox ;-;
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

    if data.get("author", None) is None or data.get("author").get("id", None) is None:
        return {"success": 0, "message": "Missing Author"}, 400

    made_by = data.get("author").get("id")
    response = {}
    try:
        match like_type:
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
    except IntegrityError:
        response = {"success": 0, "message": "Already liked"}

    return response


def make_follow(json, author_id):
    pass


# todo fix later too tired right now
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

    return {"message": "Comment made successfully."}, 201
