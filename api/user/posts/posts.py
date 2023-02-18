from flask import Blueprint, jsonify, request
from .model import Post
from api.app import db
from api.utils import get_pagination_params, Visibility
from api.user.author.model import Author
# note: this blueprint is usually mounted under  URL prefix
posts_bp = Blueprint("posts", __name__)


# Temporary endpoint to make new posts using postman
@posts_bp.route("/admin/posts/create", methods = ["POST"])
def create_temp_post():
    data = request.json
    published = data.get("published")
    title = data.get("title")
    origin = data.get("origin")
    source = data.get("source")
    description = data.get("description")
    contentType = data.get("contentType")
    content = data.get("content")
    categories = ",".join(data.get("categories"))
    visibility = data.get("visibility")
    unlisted = data.get("unlisted")
    author_id = data.get("author").get("id")

    post = Post(published=published, 
                title=title, 
                origin=origin, 
                source=source, 
                description=description, 
                content=content, 
                contentType=contentType,
                categories=categories,
                visibility=visibility,
                unlisted=unlisted,
                author_id=author_id)
    
    db.session.add(post)
    db.session.commit()

    return {"Success": 1}


@posts_bp.route("/<string:author_id>/posts/<string:post_id>", methods=["GET"])
def get_post(author_id: str, post_id: str):
    """get the public post whose id is POST_ID"""
    # author_id in database is complete url
    author = Author.query.filter_by(object_id=author_id).first()
    post_search = Post.query.filter_by(object_id=post_id, author_id=author.id).first_or_404()
    post = post_search.getJSON()

    return post


@posts_bp.route("/<string:author_id>/posts/<string:post_id>", methods=["POST"])
def edit_post(author_id: str, post_id: str):
    """update the post whose id is POST_ID (must be authenticated)"""
    pass


@posts_bp.route("/<string:author_id>/posts/<string:post_id>", methods=["DELETE"])
def delete_post(author_id: str, post_id: str):
    """remove the post whose id is post_id"""
    pass


@posts_bp.route("/<string:author_id>/posts/<string:post_id>", methods=["PUT"])
def create_post(author_id: str, post_id: str):
    """create a post where its id is post_id"""
    pass


@posts_bp.route("/<string:author_id>/posts", methods=["POST"])
def create_post_auto_gen_id(author_id: str):
    """create a new post but generate a new id"""
    pass


@posts_bp.route("/<string:author_id>/posts", methods=["GET"])
def get_recent_posts(author_id: str):
    """get the recent posts from author author_id (paginated)"""
    pagination = get_pagination_params()
    pass


@posts_bp.route("/<string:author_id>/posts/<string:post_id>/image", methods=["GET"])
def post_as_base64_img(author_id: str, post_id: str):
    """
    get the public post converted to binary as an image
     -> return 404 if not an image
    The end point decodes image posts as images. This allows the use of image tags in markdown.
    You can use this to proxy or cache images.
    """
    pass


@posts_bp.route("/<string:author_id>/inbox", methods=["POST"])
def send_like(author_id: str):
    """send a like object to author_id"""
    # todo (matt): why doesn't this have post id in the URL?
    pass


@posts_bp.route("/<string:author_id>/posts/<string:post_id>/likes", methods=["GET"])
def get_likes(author_id: str, post_id: str):
    """a list of likes from other authors on AUTHOR_ID’s post POST_ID"""
    pass


@posts_bp.route("/<string:author_id>/liked", methods=["GET"])
def get_author_likes(author_id: str):
    """
    list what public things AUTHOR_ID liked.

    It’s a list of of likes originating from this author
    Note: be careful here private information could be disclosed.
    """
    pass


@posts_bp.route("/<string:author_id>/inbox", methods=["GET"])
def get_inbox(author_id: str):
    """if authenticated get a list of posts sent to AUTHOR_ID (paginated)"""
    pagination = get_pagination_params()
    pass


@posts_bp.route("/<string:author_id>/inbox", methods=["POST"])
def post_inbox(author_id: str):
    """
    if the type is “post” then add that post to AUTHOR_ID’s inbox
    if the type is “follow” then add that follow is added to AUTHOR_ID’s inbox to approve later
    if the type is “like” then add that like to AUTHOR_ID’s inbox
    if the type is “comment” then add that comment to AUTHOR_ID’s inbox
    """
    pass


@posts_bp.route("/<string:author_id>/inbox", methods=["DELETE"])
def clear_inbox(author_id: str):
    """clear the inbox"""
    pass
