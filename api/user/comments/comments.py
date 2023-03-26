from flask import Blueprint, request
from flask_login import login_required
from flasgger import swag_from
from api import basic_auth, db
from api.user.comments.model import Comment
from api.user.comments.docs import *
from api.user.posts.model import Post
from api.utils import get_pagination_params

comments_bp = Blueprint("comments", __name__)


@comments_bp.route("/<string:author_id>/posts/<string:post_id>/comments", methods=["GET"])
@swag_from(
    {
        "tags": ["Comments"],
        "description": "Returns a paginated list of comments made on the post having id post_id authored by author_id.",
        "parameters": [
            {
                "in": "path",
                "name": "author_id",
                "type": "string",
                "required": "true",
                "description": "Author id of the author of the post",
            },
            {
                "in": "path",
                "name": "post_id",
                "type": "string",
                "required": "true",
                "description": "Post id of the post commented on",
            },
        ],
        "responses": {200: {"description": "A List of comments", "schema": comments_schema}},
    }
)
@basic_auth.required
def get_comments(author_id: str, post_id: str):
    """Get the list of comments of the post whose id is POST_ID (paginated)"""

    post = Post.query.filter_by(id=post_id).first()

    if not post:
        return {"message": "Post not found."}, 404

    comments = post.comments.paginate(**get_pagination_params().dict).items
    comment_list = []

    # If author (local or remote) is missing, skip that comment
    for comment in comments:
        comment_json = comment.getJSON()
        if not comment_json["author"]:
            continue
        comment_list.append(comment_json)

    json = {
        "type": "comments",
        "page": get_pagination_params().page,
        "size": get_pagination_params().per_page,
        "post": post.url,
        "id": post.url + "/comments",
        "comments": comment_list,
    }

    return json


@comments_bp.route("/<string:author_id>/posts/<string:post_id>/comments", methods=["POST"])
@login_required
def post_comment(author_id: str, post_id: str):
    """if you post an object of “type”:”comment”, it will add your comment to the post whose id is POST_ID"""

    data = request.json

    try:
        comment = Comment(
            published=data["published"],
            comment=data["comment"],
            contentType=data["contentType"],
            post_id=post_id,
            author_id=data["author"]["id"],
        )
    except Exception:
        return {"message": "Bad request."}, 400

    db.session.add(comment)
    db.session.commit()

    return {"message": "Commented successfully."}, 200
